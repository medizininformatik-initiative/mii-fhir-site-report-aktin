FROM python:3.9

COPY . /opt/reportclient
RUN pip install requests==2.22.0
RUN useradd -r -s /bin/false 10001
RUN chown -R 10001:10001 /opt/reportclient

WORKDIR /opt/reportclient

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh 

USER 10001

ENTRYPOINT ["docker-entrypoint.sh"]