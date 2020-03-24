
CURRENT_PATH=$(shell pwd)
PROJECT_FOLDER="."
DOCKERFILE_PATH="Dockerfile"

CONTAINER_NAME=evalytics
IMAGE_VERSION=0.1
PORT=8080

build:
	docker build . \
		--file $(DOCKERFILE_PATH) \
		--tag $(CONTAINER_NAME):$(IMAGE_VERSION)

run-server:
	docker run -d \
		--volume $(CURRENT_PATH)/server:/usr/evalytics \
		--publish $(PORT):$(PORT) \
		--name $(CONTAINER_NAME) \
		-ti $(CONTAINER_NAME):$(IMAGE_VERSION)

start-server:
	docker start $(CONTAINER_NAME)

stop-server:
	docker stop $(CONTAINER_NAME)

remove-server-container:
	docker rm $(CONTAINER_NAME)