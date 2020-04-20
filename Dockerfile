FROM python:3.7

ARG BUILD_ENV=dev

RUN mkdir -p /usr/app
COPY . /usr/app

EXPOSE 8080
ENV PYTHONPATH /usr/app
WORKDIR /usr/app

RUN pip3 install --no-cache-dir -r requirements/${BUILD_ENV}.txt

ENTRYPOINT ["python3", "server.py"]
