# Automated MII Site Reports via AKTIN

This repository contains the two clients. 

- **A central client "central-broker-client"**, which collects the site reports submitted to the central AKTIN broker, downloads them and saves them to a folder.
- **A decentral client "site-cleint"**, which connects to the local FHIR Server of the DIC, collects the capability statement, executes the queries in the report-queries.json of this repository,
and sends the finished report to the configured central AKTIN broker.


## Setting up the decentral site-client in a DIC

The client comes packaged in a docker image and can be configured via environment variables.

1. Checkout the version you would like to install by checking out the respective git tag `git checkout tags/<tag-here - e.g. v0.3.0>`

2. Set the enviroment variables in your .env file according to your requirements (explanation see "Overview Configuration Variables" below)

3. Start the process by executing `docker-compose up`

4. Check with the central team administering the central AKTIN broker if your report was successfully submitted

5. Create a cronjob similar to the `crontab` file in this repository to run the program periodically

Note: If you are using the standard installation of the feasibility triangle from here: https://github.com/medizininformatik-initiative/feasibility-deploy, please ensure that you start the container here as part of the correct docker-compose project (e.g. COMPOSE_PROJECT=mii-deploy).
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
