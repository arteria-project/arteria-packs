FROM python:2.7

RUN apt-get update

# setup arteria-runfolder service
# TODO Specify version to be installed here!
RUN git clone https://github.com/arteria-project/arteria-runfolder.git
WORKDIR arteria-runfolder
COPY app.config config/
RUN pip install -r requirements/dev .

EXPOSE 80
CMD runfolder-ws --debug --port 80 --config config/

