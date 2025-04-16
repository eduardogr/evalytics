FROM python:3.9.22-slim-bullseye AS base_builder

ARG BUILD_ENV=dev

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN mkdir -p /usr/app

COPY poetry.lock pyproject.toml /usr/app/
COPY client.py /usr/app
COPY server.py /usr/app
COPY evalytics /usr/app

ENV PYTHONPATH=/usr/app
WORKDIR /usr/app

RUN pip install poetry==2.1.2


FROM base_builder AS client

RUN poetry install --with client


FROM base_builder AS server

EXPOSE 8080

RUN poetry install --with server
