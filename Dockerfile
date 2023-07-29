FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./print_api/ /app/print_api/
COPY .env.docker /app/.env.docker
COPY app.py /app/app.py
COPY entrypoint_celery.py /app/entrypoint_celery.py
COPY entrypoint_docker.sh /app/entrypoint_docker.sh
COPY *_secret.json /app/

RUN chmod +x /app/entrypoint_docker.sh
RUN useradd celery

EXPOSE 5000

CMD ["/app/entrypoint_docker.sh"]