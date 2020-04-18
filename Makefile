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
	docker build . \
		--build-arg BUILD_ENV=$(env) \
		--file $(DOCKERFILE_PATH) \
		--tag $(CONTAINER_NAME)

google-auth:
	python3 google_auth.py

run-server:
	docker run -d \
		--volume $(CURRENT_PATH)/evalytics:/usr/app/evalytics \
		--publish $(PORT):$(PORT) \
		--name $(CONTAINER_NAME) \
		-ti $(CONTAINER_NAME)

test:
	docker exec $(CONTAINER_NAME) pytest

start-server:
	docker start $(CONTAINER_NAME)

stop-server:
	docker stop $(CONTAINER_NAME)

remove-server-container:
	docker rm $(CONTAINER_NAME)
