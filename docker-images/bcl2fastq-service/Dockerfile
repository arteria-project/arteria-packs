From centos:7

workdir /tmp
RUN yum install -y epel-release
RUN yum update -y
RUN yum install -y unzip python-pip python-virtualenv git gcc-c++ wget python-pathlib2
COPY local_files/bcl2fastq2-v2-20-0-linux-x86-64.zip  bcl2fastq2-v2-20-0-linux-x86-64.zip
RUN unzip bcl2fastq2-v2-20-0-linux-x86-64.zip
RUN yum install -y bcl2fastq2-v2.20.0.422-Linux-x86_64.rpm

# setup arteria-runfolder service
WORKDIR /
RUN git clone https://github.com/arteria-project/arteria-bcl2fastq.git
RUN echo "pathlib2" >> ./arteria-bcl2fastq/requirements/dev
RUN echo "requests<2.28" >> ./arteria-bcl2fastq/requirements/dev
RUN echo "PyYAML==5.2" >> ./arteria-bcl2fastq/requirements/dev
RUN echo "certifi==2017.11.5" >> ./arteria-bcl2fastq/requirements/dev
RUN pip install -r ./arteria-bcl2fastq/requirements/dev ./arteria-bcl2fastq
COPY app.config ./arteria-bcl2fastq/config/
RUN mkdir /bcl2fastq-logs

EXPOSE 80
CMD bcl2fastq-ws --debug --port 80 --config ./arteria-bcl2fastq/config/
