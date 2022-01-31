#!/bin/bash

FHIR_BASE_URL=${FHIR_BASE_URL:-"http://fhir-server:8080/fhir"}
BROKER_ENDPOINT_URI=${BROKER_ENDPOINT_URI:-"http://aktin-broker:8080/broker/"}
CLIENT_AUTH_PARAM=${CLIENT_AUTH_PARAM:-"xxxApiKey123"}

python3 aktin-fhir-mii-report-client.py --fhirurl $FHIR_BASE_URL --brokerurl $BROKER_ENDPOINT_URI --apikey $CLIENT_AUTH_PARAM