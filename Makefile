
CONTAINER_SERVER_NAME=server
CONTAINER_CLIENT_NAME=client

env ?= dev # get from cl or 'dev' by default

# make
# make build
# make build env=prod
build:
	docker-compose build \
	    --build-arg BUILD_ENV=$(env) \
		$(CONTAINER_SERVER_NAME)  && \
	docker-compose build \
		--build-arg BUILD_ENV=$(env) \
		$(CONTAINER_CLIENT_NAME)

build-force:
	docker-compose build --force \
	    --build-arg BUILD_ENV=$(env) \
		$(CONTAINER_SERVER_NAME) && \
	docker-compose build --force \
		--build-arg BUILD_ENV=$(env) \
		$(CONTAINER_CLIENT_NAME)

up:
	docker-compose up -d $(CONTAINER_SERVER_NAME)

down:
	docker-compose down

google-auth:
	python3 scripts/google_auth.py

run-client:
	docker compose run --rm $(CONTAINER_CLIENT_NAME) poetry run client.py $(ARGS)

run-server:
	docker compose run --rm $(CONTAINER_SERVER_NAME) poetry run python server.py

poetry-check:
	poetry check

poetry-install:
	poetry install

poetry-install-dev:
	poetry install --with dev

test:
	poetry run pytest $(ARGS)