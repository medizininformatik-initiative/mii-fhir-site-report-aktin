FROM python:3.9

COPY . /opt/reportclient
RUN pip install requests==2.22.0
RUN groupadd -r reporter && useradd -r -s /bin/false -g reporter reporter
RUN chown -R reporter:reporter /opt/reportclient

WORKDIR /opt/reportclient

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh 

USER reporter

ENTRYPOINT ["docker-entrypoint.sh"]