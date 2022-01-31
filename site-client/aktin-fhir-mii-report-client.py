import requests
import json
import argparse

fhir_base_url = "http://localhost:8081/fhir"
aktin_broker_url = "http://localhost:8082/broker/"
aktin_broker_api_key = "xxxApiKey123"

parser = argparse.ArgumentParser()
parser.add_argument('--fhirurl', help='base url of your local fhir server')
parser.add_argument('--brokerurl', help='base url of the central aktin broker')
parser.add_argument('--apikey', help='your api key')
args = vars(parser.parse_args())

fhir_base_url = args["fhirurl"]
aktin_broker_url = args["brokerurl"]
aktin_broker_api_key = args["apikey"]

aktin_broker_node_url = f'{aktin_broker_url}my/node/miireport'

with open('report-queries.json') as json_file:
    report = json.load(json_file)
    queries = report["queries"]
    for query in queries:
        resp = requests.get(fhir_base_url + query["query"]).json()
        query['response'] = resp['total']

headers = {'Authorization': f"Bearer {aktin_broker_api_key}"}
resp = requests.put(aktin_broker_node_url, json=json.dumps(report), headers=headers)
print(resp.text)
