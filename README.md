# Storage Module

This module is responsible for storing the apk and the privacy policy of the applications.


## Getting Started

### Prerequisites:

There are no specific prerequisites for this module.

### Installing:

1. Login to Docker Hub:

`docker login`

2. Pull the image of download module:

`docker pull cliip/storage_v2`

### Run:

The following command will run the container:

(Nota: Puede estar almacenado también en cliip/storage_v2)
`docker run --network host cliip/platform:storage_v2`

### Build:

To build the image you must first run the following dockerfile using this command:

`docker build -t cliip/platform:storage_v2 .`

```
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
```
### Upload:

1. Login to Docker Hub:

`docker login`

2. Pull the image of storage module:

`docker push cliip/platform:storage`

### Documentation
This section explains in more detail the functions and interfaces
of each download module component, as well as the organization
of all necessary files in their respective directories.

![Error while loading the image](storag_ module.png)
~~~
Figure 1. Components of the storage module
~~~

**1. storage/**

   This is the main directory where all the files needed to run the component are.
    
   **_1.1 storage/api.py_**
    
   This is the file that contains the API code for the storage module.
        
   **_1.3 storage/requirements.txt_**
    
   This file contains all the dependencies that need to be installed in the
   container.
     
   **_1.4 storage/script.sh_**
    
   This file contains the commands that are executed when the container is 
   started.
    
**2. Downloads/**

   This is the file where all the apk files are storaged

## Logging

The following logs' fields are related to 'Storage' container, even though some are common to other containers, e.g json.apk. These fields can be used to filter logs on Kibana platform.

'json.apk' -> APK's name  
'json.version' -> App’s version  
'json.container' -> 'storage'  
'json.type' -> Format of privacy policies doc: can be html or txt  
'json.testing_label' -> Testing label
