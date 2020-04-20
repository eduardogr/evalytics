CURRENT_PATH=$(shell pwd)
PROJECT_FOLDER="."
DOCKERFILE_PATH="Dockerfile"

CONTAINER_NAME=evalytics
PORT=8080

env ?= dev # get from cl or 'dev' by default

# make
# make build
# make build env=prod
build:
	docker-compose build \
	    --build-arg BUILD_ENV=$(env) \
		$(CONTAINER_NAME)

build-force:
	docker-compose build --force \
	    --build-arg BUILD_ENV=$(env) \
		$(CONTAINER_NAME)

up:
	docker-compose up -d

down:
	docker-compose down

test:
	docker-compose exec $(CONTAINER_NAME) pytest

google-auth:
	python3 google_auth.py
