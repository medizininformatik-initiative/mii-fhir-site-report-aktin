import requests
import json
# import os
import time
import argparse
from datetime import datetime
from requests.auth import HTTPBasicAuth
from json.decoder import JSONDecodeError

parser = argparse.ArgumentParser()
parser.add_argument('--fhirurl', help='base url of your local fhir server', default="http://localhost:8081/fhir")
parser.add_argument('--fhiruser', help='basic auth user fhir server', nargs="?", default="")
parser.add_argument('--fhirpw', help='basic auth pw fhir server', nargs="?", default="")
parser.add_argument('--fhirtoken', help='token auth fhir server', nargs="?", default="")
parser.add_argument('--brokerurl', help='base url of the central aktin broker', default="http://localhost:8082/broker/")
parser.add_argument('--apikey', help='your api key', default="xxxApiKey123")
parser.add_argument('--httpsproxyaktin', help='your https proxy url for your aktin connection - None if not set here', nargs="?", default=None)
parser.add_argument('--httpproxyfhir', help='http proxy url for your fhir server - None if not set here', nargs="?", default=None)
parser.add_argument('--httpsproxyfhir', help='https proxy url for your fhir server - None if not set here', nargs="?", default=None)
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

mii_relevant_resources = ['Patient', 'Encounter' 'Observation', 'Procedure', 'Consent',
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


def execute_status_queries(queries):

    for query in queries:
        start = time.time()
        if fhir_token is not None:
            resp = requests.get(f'{fhir_base_url}{query["query"]}', headers={'Authorization': f"Bearer {fhir_token}", 'Prefer': 'handling=strict'},
                                proxies=proxies_fhir)
        else:
            resp = requests.get(f'{fhir_base_url}{query["query"]}', headers={"Prefer": 'handling=strict'}, auth=HTTPBasicAuth(
                fhir_user, fhir_pw), proxies=proxies_fhir)

        query['status'] = "success"

        if resp.status_code != 200:
            query['status'] = "failed"

        try:
            resp = resp.json()
        except JSONDecodeError:
            query['status'] = "failed"

        if query['status'] != "failed":
            query['response'] = resp['total']

        end = time.time()
        query['timeSeconds'] = end - start

def execute_capability_statement(capabilityStatement):
    if fhir_token is not None:
        resp = requests.get(f'{fhir_base_url}/metadata', headers={'Authorization': f"Bearer {fhir_token}", 'Prefer': 'handling=strict'})
    else:
        resp = requests.get(f'{fhir_base_url}/metadata', headers={"Prefer": 'handling=strict'}, auth=HTTPBasicAuth(
            fhir_user, fhir_pw))

    if resp.status_code != 200:
        capabilityStatement['status'] = "failed"

    try:
        resp = resp.json()
    except JSONDecodeError:
        capabilityStatement['status'] = "failed"
        return

    capabilityStatement['software']['name'] = resp['software']['name']
    capabilityStatement['software']['version'] = resp['software']['version']

    for resource in resp['rest'][0]['resource']:

        if resource["type"] in mii_relevant_resources:
            capabilityStatement['searchParams'].append(resource)


with open('report-queries.json') as json_file:
    report = json.load(json_file)
    report['datetime'] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    execute_status_queries(report["statusQueries"])
    execute_capability_statement(report['capabilityStatement'])


headers = {'Authorization': f"Bearer {aktin_broker_api_key}"}
resp = requests.put(aktin_broker_node_url,
                    json=json.dumps(report), headers=headers, proxies=proxy_aktin)
