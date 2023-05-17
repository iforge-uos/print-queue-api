FROM python:3.10

WORKDIR /app
COPY print_api/ /app/print_api/
COPY requirements.txt requirements.txt
COPY .env .env
COPY entrypoint_api.py app.py

RUN pip install -r requirements.txt

EXPOSE 5000