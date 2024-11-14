FROM python:3.7
WORKDIR /app

RUN apt-get update && \
  apt-get upgrade -y && \
  apt install -y python3 python3-dev python3-pip nano

# User and password as arguments to build, so they are not
# leaked in the repository.
ARG USERNAME=PrivApp
ARG PASSWORD=FscU2W7xPHSm

RUN apt-get install git -y && \
  git clone https://$USERNAME:$PASSWORD@gitlab.com/cliip/storage_v2 && \
  mv storage_v2/* . && \
  rm -r storage_v2 && \
  git clone https://$USERNAME:$PASSWORD@gitlab.com/privapp/logging && \
  rm -r */.git && \
  apt-get remove git -y
RUN pip3 install -r requirements.txt
RUN chmod +x script.sh

WORKDIR /app/logging
#RUN mkdir log

WORKDIR /app/logging/agent
RUN apt-get install curl -y && \
	curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.3.2-amd64.deb && \
	dpkg -i filebeat-7.3.2-amd64.deb && \
	apt remove curl -y && \
	cp filebeat.yml /etc/filebeat && \
	cp update_filebeat.py /etc/filebeat

WORKDIR /app
CMD ./script.sh

