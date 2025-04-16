FROM python:3.9.22-slim-bullseye

ARG BUILD_ENV=dev

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN mkdir -p /usr/app

COPY poetry.lock pyproject.toml /usr/app/
COPY server.py /usr/app
COPY evalytics /usr/app

EXPOSE 8080
ENV PYTHONPATH=/usr/app
WORKDIR /usr/app

RUN pip install poetry==2.1.2
RUN poetry install

ENTRYPOINT ["python3", "server.py"]
