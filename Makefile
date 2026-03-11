.PHONY: build-images upload_images deploy-local

## Contruir las imágenes Docker del proyecto
build-images:
	bash scripts/build-images.sh

## Subir las imágenes Docker a Docker Hub
upload-images:
	bash scripts/upload-images.sh

## Desplegar la aplicación localmente usando Docker Compose
deploy-local:
	docker compose -f docker-compose-local.yml up -d --build