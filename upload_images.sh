#!/bin/bash
set -e

DOCKER_USERNAME="alk3rg" 

# Lista de imágenes
IMAGES=(
    "techlab-databroker"
    "techlab-mocknotify"
    "techlab-mqttbroker"
    "techlab-microfrontend"
)

for IMAGE in "${IMAGES[@]}"; do
    
    # Etiquetando la imagen local con el formato de Docker Hub
    echo "Etiquetando $IMAGE:latest como $DOCKER_USERNAME/$IMAGE:latest..."
    docker tag "$IMAGE:latest" "$DOCKER_USERNAME/$IMAGE:latest"
    # Subiendo la imagen a Docker Hub
    docker push "$DOCKER_USERNAME/$IMAGE:latest"
    
    echo "$IMAGE subida correctamente."
done

echo "-------------------------------------------------"
echo "Todas las imágenes han sido subidas exitosamente."