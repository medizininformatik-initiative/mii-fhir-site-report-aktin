#!/bin/bash

FHIR_BASE_URL=${FHIR_BASE_URL:-"http://fhir-server:8080/fhir"}
BROKER_ENDPOINT_URI=${BROKER_ENDPOINT_URI:-"http://aktin-broker:8080/broker/"}
CLIENT_AUTH_PARAM=${CLIENT_AUTH_PARAM:-"xxxApiKey123"}
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

if [[ $SEARCH_PAT_YEAR_FACILITY == "true" ]] || [[ $SEARCH_PAT_YEAR_FACILITY == "True" ]]
then
PAT_YEAR_FACILITY="--patyearfacility"
fi

if [[ $EXEC_YEAR_QUERIES == "true" ]] || [[ $SEARCH_PAT_YEAR_FACILITY == "True" ]]
then
EXEC_YEAR_QUERIES_TOKEN="--execyearqueries"
fi

if [[ $EXEC_PAT_YEAR_QUERIES == "true" ]] || [[ $EXEC_PAT_YEAR_QUERIES == "True" ]]
then
EXEC_PAT_YEAR_QUERIES_TOKEN="--execpatyearqueries"
fi

echo "Begin generating report..."

if [[ $SEND_REPORT == "true" ]] || [[ $SEND_REPORT == "True" ]]
then
python3 -u aktin-fhir-mii-report-client.py --fhirurl $FHIR_BASE_URL --brokerurl $BROKER_ENDPOINT_URI --apikey $CLIENT_AUTH_PARAM --fhiruser $FHIR_USER \
--fhirpw $FHIR_PW --fhirtoken $FHIR_TOKEN --httpsproxyaktin $AKTIN_HTTPS_PROXY --httpproxyfhir $FHIR_PROXY_HTTP --httpsproxyfhir $FHIR_PROXY_HTTPS \
--sendreport $PAT_YEAR_FACILITY $EXEC_YEAR_QUERIES_TOKEN $EXEC_PAT_YEAR_QUERIES_TOKEN
else
python3 -u aktin-fhir-mii-report-client.py --fhirurl $FHIR_BASE_URL --brokerurl $BROKER_ENDPOINT_URI --apikey $CLIENT_AUTH_PARAM --fhiruser $FHIR_USER \
--fhirpw $FHIR_PW --fhirtoken $FHIR_TOKEN --httpsproxyaktin $AKTIN_HTTPS_PROXY --httpproxyfhir $FHIR_PROXY_HTTP --httpsproxyfhir $FHIR_PROXY_HTTPS \
$PAT_YEAR_FACILITY $EXEC_YEAR_QUERIES_TOKEN $EXEC_PAT_YEAR_QUERIES_TOKEN
fi

echo "Finished generating report"
