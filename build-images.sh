#!/bin/bash
set -e  

# Construir imágenes del backend
docker build -t techlab-databroker:latest -f backend/Dockerfile.databroker backend/

docker build -t techlab-mocknotify:latest -f backend/Dockerfile.mocknotify backend/

docker build -t techlab-mqttbroker:latest -f backend/Dockerfile.mqttbroker backend/

# Construir imagen del microfrontend
docker build -t techlab-microfrontend:latest -f microfrontend/Dockerfile microfrontend/

echo "Imágenes docker construidas con éxito"

