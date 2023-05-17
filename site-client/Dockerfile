FROM python:3.9

RUN apt install ca-certificates
COPY ./*.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

RUN pip install requests==2.22.0
RUN pip install pandas==1.4.4
RUN useradd -r -s /bin/false 10001
COPY . /opt/reportclient
RUN chown -R 10001:10001 /opt/reportclient
WORKDIR /opt/reportclient

COPY docker-entrypoint.sh /usr/local/bin/
COPY report-queries.json /opt/reportclient/report-queries.json
RUN chown 10001:10001 /opt/reportclient/report-queries.json
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER 10001

ENTRYPOINT ["docker-entrypoint.sh"]