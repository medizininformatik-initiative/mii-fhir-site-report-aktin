import requests
from datetime import datetime
import xml.etree.ElementTree as ET
import argparse

nodes = []
aktin_broker_base_url = "http://localhost:8082/broker/node/"
aktin_broker_api_key = "xxxApiKeyAdmin123"


parser = argparse.ArgumentParser()
parser.add_argument('--brokerurl', help='base url of the central aktin broker')
parser.add_argument('--apikey', help='your api key')
args = vars(parser.parse_args())
aktin_broker_base_url = args["brokerurl"]
aktin_broker_api_key = args["apikey"]


headers = {'Authorization': f"Bearer {aktin_broker_api_key}"}
resp = requests.get(aktin_broker_base_url, headers=headers)
tree = ET.fromstring(resp.text)

for child in tree:

    node_name = child.find("{http://aktin.org/ns/exchange}clientDN").text.split("CN=", 1)[1].split(",")[0]

    nodes.append({"node_id": child.find("{http://aktin.org/ns/exchange}id").text,
                  "node_name": node_name
                  })


for node in nodes:
    out_file_name = f'reports/mii-report-site-{node["node_name"]}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
    mii_report = {}

    aktin_broker_node_report_url = f'{aktin_broker_base_url}{node["node_id"]}/miireport'

    headers = {'Authorization': f"Bearer {aktin_broker_api_key}"}
    resp = requests.get(aktin_broker_node_report_url, headers=headers).json()

    with open(out_file_name, 'w', encoding='utf-8') as out_file:
        out_file.write(resp)
