FROM python:3.7

EXPOSE 8080

RUN mkdir -p /usr/evalytics
WORKDIR /usr/evalytics

COPY server .

RUN pip install --no-cache-dir -r requirements/prod.txt

ENTRYPOINT ["python3", "main.py"]
