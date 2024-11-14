#!/bin/bash 
set -m 
python3 logging/agent/update_filebeat.py & 
python3 api.py

