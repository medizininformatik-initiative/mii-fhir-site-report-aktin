import requests
import json
import argparse
import os
from datetime import datetime
from requests.auth import HTTPBasicAuth
from json.decoder import JSONDecodeError


parser = argparse.ArgumentParser()
parser.add_argument('--fhirurl', help='base url of your local fhir server', default="http://localhost:8081/fhir")
parser.add_argument('--fhiruser', help='basic auth username of your local fhir server')
parser.add_argument('--fhirpass', help='basic auth password of your local fhir server')
parser.add_argument('--fhirnoverify', help='disable ssl certificate verification for your local fhir server', action='store_false')
parser.add_argument('--brokerurl', help='base url of the central aktin broker', default="http://localhost:8082/broker/")
parser.add_argument('--apikey', help='your api key', default="xxxApiKey123")
args = vars(parser.parse_args())

fhir_base_url = args["fhirurl"]
aktin_broker_url = args["brokerurl"]
aktin_broker_api_key = args["apikey"]
if "fhiruser" in args and "fhirpass" in args:
    fhir_username = args["fhiruser"]
    fhir_password = args["fhirpass"]
elif "FHIR_USERNAME" in os.environ and "FHIR_PASSWORD" in os.environ:
    fhir_username = os.environ["FHIR_USERNAME"]
    fhir_password = os.environ["FHIR_PASSWORD"]
fhir_verify = args["fhirnoverify"]
if "FHIR_NOVERIFY" in os.environ:
    fhir_verify = False if os.environ["FHIR_NOVERIFY"] == True else True
if not fhir_verify:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

aktin_broker_node_url = f'{aktin_broker_url}my/node/miireport'

with open('report-queries.json') as json_file:
    report = json.load(json_file)
    report['datetime'] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    queries = report["queries"]
    for query in queries:
        url = requests.compat.urljoin(fhir_base_url, query["query"])
        if fhir_username and fhir_password:
            resp = requests.get(url, auth=HTTPBasicAuth(fhir_username, fhir_password), verify=fhir_verify)
        else:
            resp = requests.get(url + query["query"], verify=fhir_noverify)
        try:
            resp = resp.json()
        except JSONDecodeError as e:
            print(f"Invalid response: {e} - {resp}")
        query['response'] = resp['total']

headers = {'Authorization': f"Bearer {aktin_broker_api_key}"}
resp = requests.put(aktin_broker_node_url, json=json.dumps(report), headers=headers)
