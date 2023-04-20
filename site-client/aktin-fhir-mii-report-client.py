import requests
import json
# import os
import time
import argparse
from datetime import datetime, date
from requests.auth import HTTPBasicAuth
from json.decoder import JSONDecodeError
from urllib.parse import urlparse
from urllib.parse import parse_qs
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--fhirurl', help='base url of your local fhir server',
                    default="http://localhost:8081/fhir")
parser.add_argument(
    '--fhiruser', help='basic auth user fhir server', nargs="?", default="")
parser.add_argument(
    '--fhirpw', help='basic auth pw fhir server', nargs="?", default="")
parser.add_argument(
    '--fhirtoken', help='token auth fhir server', nargs="?", default=None)
parser.add_argument('--brokerurl', help='base url of the central aktin broker',
                    default="http://localhost:8082/broker/")
parser.add_argument('--apikey', help='your api key', default="xxxApiKey123")
parser.add_argument('--httpsproxyaktin',
                    help='your https proxy url for your aktin connection - None if not set here', nargs="?", default=None)
parser.add_argument(
    '--httpproxyfhir', help='http proxy url for your fhir server - None if not set here', nargs="?", default=None)
parser.add_argument('--httpsproxyfhir',
                    help='https proxy url for your fhir server - None if not set here', nargs="?", default=None)
parser.add_argument(
    '--sendreport', help='Boolean whether to send the report to the broker or not', action='store_true', default=False)
parser.add_argument(
    '--patyearfacility', help='Boolean whether or not to query only facility encounters for the yearly patient count', action='store_true', default=False)

args = vars(parser.parse_args())

fhir_base_url = args["fhirurl"]
fhir_user = args["fhiruser"]
fhir_pw = args["fhirpw"]
fhir_token = args["fhirtoken"]
aktin_broker_url = args["brokerurl"]
aktin_broker_api_key = args["apikey"]
https_proxy_aktin = args["httpsproxyaktin"]
http_proxy_fhir = args["httpproxyfhir"]
https_proxy_fhir = args["httpsproxyfhir"]
send_report = args["sendreport"]
pat_year_with_facility = args["patyearfacility"]

mii_relevant_resources = ['Patient', 'Encounter', 'Observation', 'Procedure', 'Consent',
                          'Medication', 'MedicationStatement', 'MedicationAdministration', 'Condition',
                          'Specimen', 'DiagnosticReport', 'ResearchSubject', 'ServiceRequest']

proxies_fhir = {
    "http": http_proxy_fhir,
    "https": https_proxy_fhir
}

proxy_aktin = {
    "https": https_proxy_aktin
}

aktin_broker_node_url = f'{aktin_broker_url}my/node/miireport'


def query_successful(query_url, resp_links):

    self_link = ""
    for link in resp_links:
        if link['relation'] == 'self':
            self_link = link['url']

    parsed_url = urlparse(query_url)
    query_url_params = parse_qs(parsed_url.query)

    parsed_url = urlparse(self_link)
    self_link_params = parse_qs(parsed_url.query)

    for param in query_url_params:
        if param not in self_link_params:
            return False

    return True


def convert_report_to_csv(site_report, report_time):
    df = pd.json_normalize(site_report['statusQueries'])
    df = df.drop('dateParam', axis=1)
    df = df.drop('startYear', axis=1)
    df.to_csv(f'reports/site-report-{report_time}.csv')

def execute_query(query):
    start = time.time()

    query_url = f'{fhir_base_url}{query}'

    print(f'executing status report query: {query_url}')

    if fhir_token is not None:
        resp = requests.get(query_url, headers={'Authorization': f"Bearer {fhir_token}", 'Prefer': 'handling=strict'},
                            proxies=proxies_fhir, timeout=None)
    else:
        resp = requests.get(query_url, headers={"Prefer": 'handling=strict'}, auth=HTTPBasicAuth(
            fhir_user, fhir_pw), proxies=proxies_fhir, timeout=None)

    resp_object = {}
    resp_object['status'] = "success"

    if resp.status_code != 200:
        resp_object['status'] = "failed"

    try:
        resp_object['json'] = resp.json()

        if 'link' in resp_object['json'].keys() and not query_successful(query_url, resp_object['json']['link']):
            resp_object['status'] = "failed"
    except JSONDecodeError:
        resp_object['status'] = "failed"

    end = time.time()
    resp_object['timeSeconds'] = end - start

    return resp_object

def execute_year_query(query):
    cur_year = query['startYear']
    last_year = date.today().year
    query['responseByYear'] = {}

    while cur_year <= last_year:
        parsed_url = urlparse(query['query'])
        year_query = f'{parsed_url.path}?{query["dateParam"]}={str(cur_year)}&{parsed_url.query}'
        resp = execute_query(year_query)
        if resp['status'] != "failed":
            query['responseByYear'][str(cur_year)] = resp['json']['total']
        cur_year = cur_year + 1

    return query


def execute_status_queries(status_queries):

    for query in status_queries:

        if 'startYear' in query:
            execute_year_query(query)
        else:
            resp = execute_query(query['query'])
            query['status'] = resp['status']

            if resp['status'] != "failed":
                query['timeSeconds'] = resp['timeSeconds']
                query['response'] = resp['json']['total']


def get_next_link(link_elem):
    for elem in link_elem:
        if elem['relation'] == 'next':
            return elem['url']

    return None


def page_through_results_and_collect(resp_json, pat_ids):

    if 'entry' not in resp_json:
        return pat_ids

    next_link = get_next_link(resp_json['link'])
    result_list = list(map(lambda entry: entry['resource']['subject']['reference'].split(
        '/')[1], resp_json['entry']))
    pat_ids.update(result_list)

    while next_link:
        if fhir_token is not None:
            resp = requests.get(next_link, headers={'Authorization': f"Bearer {fhir_token}", 'Prefer': 'handling=strict'},
                                proxies=proxies_fhir)
        else:
            resp = requests.get(next_link, headers={"Prefer": 'handling=strict'}, auth=HTTPBasicAuth(
                                fhir_user, fhir_pw), proxies=proxies_fhir)

        if 'entry' not in resp_json:
            return pat_ids

        result_list_temp = list(map(lambda entry: entry['resource']['subject']['reference'].split(
            '/')[1], resp.json()['entry']))
        next_link = get_next_link(resp.json()['link'])
        pat_ids.update(result_list_temp)

    return pat_ids


def execute_pat_year_queries():

    cur_year = 2000
    last_year = date.today().year
    pats_by_year = {}

    while cur_year <= last_year:
        pat_ids = set()
        query = f'/Encounter?date={str(cur_year)}&_count=500'

        if pat_year_with_facility:
            query = f'/Encounter?type=http://fhir.de/CodeSystem/Kontaktebene|einrichtungskontakt&date={str(cur_year)}&_count=500'
        
        resp = execute_query(query)
        resp_json = resp['json']
        pat_ids = page_through_results_and_collect(resp_json, pat_ids)
        pats_by_year[str(cur_year)] = len(pat_ids)
        cur_year = cur_year + 1

    return pats_by_year


def execute_capability_statement(capabilityStatement):

    resp = execute_query('/metadata')

    if resp['status'] != "failed":

        capabilityStatement['software']['name'] = resp['json']['software']['name']
        capabilityStatement['software']['version'] = resp['json']['software']['version']
        capabilityStatement['instantiates'] = resp['json'].get(
            'instantiates', [])

        for resource in resp['json']['rest'][0]['resource']:

            if resource["type"] in mii_relevant_resources:
                capabilityStatement['searchParams'].append(resource)


with open('report-queries.json') as json_file:
    report = json.load(json_file)
    report['datetime'] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    execute_status_queries(report["statusQueries"])
    pats_by_year = execute_pat_year_queries()
    report['nPatientsByYear'] = pats_by_year
    execute_capability_statement(report['capabilityStatement'])


report_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

with open(f'reports/site-report-{report_time}.json', 'w') as output_file:
    output_file.write(json.dumps(report))

convert_report_to_csv(report, report_time)

if send_report:
    print(f'Sending report to central broker at: {aktin_broker_node_url}')
    headers = {'Authorization': f"Bearer {aktin_broker_api_key}"}
    resp = requests.put(aktin_broker_node_url,
                        json=json.dumps(report), headers=headers, proxies=proxy_aktin)
    print(f'Response from aktin broker: {resp.status_code}{resp.text}')

else:
    print("Not sending report - Check your local report output and then set SEND_REPORT to true once you have verified your report")
    print(f'Currently configured central broker url would be {aktin_broker_node_url}')
