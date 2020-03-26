FROM python:3.7

EXPOSE 8080

RUN mkdir -p /usr/evalytics
WORKDIR /usr/evalytics

COPY evalytics .

RUN pip install --no-cache-dir -r requirements/test.txt

ENV PYTHONPATH /usr/evalytics
ENTRYPOINT ["python3", "main.py"]
