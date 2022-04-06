import requests
import json
import argparse
from datetime import datetime
from requests.auth import HTTPBasicAuth

parser = argparse.ArgumentParser()
parser.add_argument('--fhirurl', help='base url of your local fhir server', default="http://localhost:8081/fhir")
parser.add_argument('--fhiruser', help='basic auth user fhir server', nargs="?", default="")
parser.add_argument('--fhirpw', help='basic auth pw fhir server', nargs="?", default="")
parser.add_argument('--brokerurl', help='base url of the central aktin broker', default="http://localhost:8082/broker/")
parser.add_argument('--apikey', help='your api key', default="xxxApiKey123")
parser.add_argument('--httpsproxy', help='your https proxy url', nargs="?", default="")
args = vars(parser.parse_args())

fhir_base_url = args["fhirurl"]
fhir_user = args["fhiruser"]
fhir_pw = args["fhirpw"]
aktin_broker_url = args["brokerurl"]
aktin_broker_api_key = args["apikey"]
aktin_broker_api_key = args["apikey"]
https_proxy = args["httpsproxy"]

proxies = {
    "https": https_proxy
}

aktin_broker_node_url = f'{aktin_broker_url}my/node/miireport'

with open('report-queries.json') as json_file:
    report = json.load(json_file)
    report['datetime'] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    queries = report["queries"]
    for query in queries:
        resp = requests.get(f'{fhir_base_url}{query["query"]}', auth=HTTPBasicAuth(
            fhir_user, fhir_pw), proxies=proxies).json()
        query['response'] = resp['total']

headers = {'Authorization': f"Bearer {aktin_broker_api_key}"}
resp = requests.put(aktin_broker_node_url,
                    json=json.dumps(report), headers=headers)
