#!/bin/bash

BROKER_ENDPOINT_URI=${BROKER_ENDPOINT_URI:-"http://aktin-broker:8080/broker/"}
CLIENT_AUTH_PARAM=${CLIENT_AUTH_PARAM:-"xxxApiKey123"}

python3 aktin-fhir-mii-report-broker-client.py --brokerurl $BROKER_ENDPOINT_URI --apikey $CLIENT_AUTH_PARAM