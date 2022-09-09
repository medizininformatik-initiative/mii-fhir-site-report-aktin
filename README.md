# Automated MII Site Reports via AKTIN

This repository contains the two clients. 

- **A central client "central-broker-client"**, which collects the site reports submitted to the central AKTIN broker, downloads them and saves them to a folder.
- **A decentral client "site-cleint"**, which connects to the local FHIR Server of the DIC, collects the capability statement, executes the queries in the report-queries.json of this repository,
and sends the finished report to the configured central AKTIN broker.


## Setting up the decentral site-client in a DIC

The client comes packaged in a docker image and can be configured via environment variables.

1. Checkout the version you would like to install by checking out the respective git tag `git checkout tags/<tag-here - e.g. v0.3.0>`

2. Initialise the .env file. If it already exists compare .env file to .env.default file and add any new var from .env.default to the .env file

2. Set the enviroment variables in your .env file according to your requirements (explanation see "Overview Configuration Variables" below)

3. Start the process by executing `docker-compose up`

4. By default the variable MII_REPORT_CLIENT_SEND_REPORT is set to false - this allows you to generate a report without sending it out so that you can check it manually before.

5. After a first run with MII_REPORT_CLIENT_SEND_REPORT=false - check the generated report under /reports and if satisfied change to MII_REPORT_CLIENT_SEND_REPORT=true

6. Start the process again by executing `docker-compose up`

7. Check with the central team administering the central AKTIN broker if your report was successfully submitted

8. Create a cronjob similar to the `crontab` file in this repository to run the program periodically

Note: If you are using the standard installation of the feasibility triangle from here: https://github.com/medizininformatik-initiative/feasibility-deploy, please ensure that you start the container here as part of the correct docker-compose project (e.g. COMPOSE_PROJECT=feasibility-deploy). In this case MII_REPORT_CLIENT_FHIR_BASE_URL should match the set docker BASE_URL (default: http://fhir-server:8080/fhir).
Example: `docker-compose -p $COMPONSE_PROJECT up`. the -p option then also has to be carried over to your crontab configuration.


## Overview Configuration Variables

|Environment Variable| description | default value |
|--|--|--|
|MII_REPORT_CLIENT_FHIR_BASE_URL|Local FHIR server base url e.g. see default value|http://fhir-server:8080/fhir|
|MII_REPORT_CLIENT_FHIR_USER|Basic auth user for local FHIR server|None|
|MII_REPORT_CLIENT_FHIR_PW|Basic auth password for local FHIR server|None|
|MII_REPORT_CLIENT_FHIR_TOKEN|auth token for local FHIR server|None|
|MII_REPORT_CLIENT_FHIR_PROXY_HTTP| HTTP url for proxy if used for local FHIR server|None|
|MII_REPORT_CLIENT_FHIR_PROXY_HTTPS| HTTPS url for proxy if used for local FHIR server|None|
|MII_REPORT_BROKER_ENDPOINT_URI|Url of central AKTIN broker example see default |http://aktin-broker:8080/broker/|
|MII_REPORT_CLIENT_AUTH_PARAM| Client specific API key for central AKTIN broker|xxxApiKey123|
|MII_REPORT_CLIENT_AKTIN_HTTPS_PROXY|HTTPS url for proxy if used for local connecting to central AKTIN broker server, e.g. (with user: https://user:password@proxyip:port, without user: https://proxyip:port)|None|
|MII_REPORT_CLIENT_SEND_REPORT| configures if the report should be send to the central broker, set to false to generate the report locally first|false|
