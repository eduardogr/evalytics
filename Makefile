
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

google-auth:
	python3 google_auth.py

request:
	docker-compose run $(CONTAINER_CLIENT_NAME) python3 client.py $(ARGS)

poetry-check:
	poetry check

poetry-install:
	poetry install

poetry-install-dev:
	poetry install --with dev

test:
	poetry run pytest $(ARGS)