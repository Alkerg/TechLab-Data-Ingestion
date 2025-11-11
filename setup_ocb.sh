#!/bin/bash
#git clone https://github.com/FIWARE/tutorials.Getting-Started.git
cd OrionContextBroker
git checkout NGSI-v2

export $(cat .env | grep "#" -v)
docker compose up -d