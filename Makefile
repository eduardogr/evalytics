
CONTAINER_NAME=evalytics
CONTAINER_CLIENT_NAME=evalytics-client

env ?= dev # get from cl or 'dev' by default

# make
# make build
# make build env=prod
build:
	docker-compose build \
	    --build-arg BUILD_ENV=$(env) \
		$(CONTAINER_NAME)  && \
	docker-compose build \
		--build-arg BUILD_ENV=$(env) \
		$(CONTAINER_CLIENT_NAME)

build-force:
	docker-compose build --force \
	    --build-arg BUILD_ENV=$(env) \
		$(CONTAINER_NAME) && \
	docker-compose build --force \
		--build-arg BUILD_ENV=$(env) \
		$(CONTAINER_CLIENT_NAME)

up:
	docker-compose up -d $(CONTAINER_NAME)

down:
	docker-compose down

test:
	docker-compose exec $(CONTAINER_NAME) pytest $(ARGS)

google-auth:
	python3 google_auth.py

request:
	docker-compose run $(CONTAINER_CLIENT_NAME) python3 client.py $(ARGS)