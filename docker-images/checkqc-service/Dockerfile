FROM python:3.6

RUN apt-get update

RUN pip install checkqc==v1.4.0  PyYAML==5.1b5
RUN mkdir /opt/monitored-folder
COPY config.yaml /config.yaml
EXPOSE 80
CMD checkqc-ws --config /config.yaml --debug --port 80 /opt/monitored-folder/
