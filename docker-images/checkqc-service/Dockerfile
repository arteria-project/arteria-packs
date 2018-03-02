FROM python:3.6

RUN apt-get update

RUN pip install -f https://github.com/Illumina/interop/releases/tag/v1.1.1 interop
# TODO Specify version to be installed here!
RUN pip install checkqc
RUN mkdir /opt/monitored-folder
EXPOSE 80
CMD checkqc-ws --debug --port 80 /opt/monitored-folder/

