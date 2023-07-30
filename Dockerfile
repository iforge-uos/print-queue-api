# Base Image
FROM python:3.11 as builder
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt

# Final Image
FROM python:3.11
WORKDIR /app
RUN useradd -m iforger
RUN useradd -m iforger-worker
COPY --from=builder /root/.local /home/iforger/.local
ENV PATH=/home/iforger/.local/bin:$PATH \
    PYTHONUSERBASE=/home/iforger/.local \
    PYTHONPATH=/home/iforger/.local/lib/python3.11/site-packages
ENV PATH=/home/iforger/.local/bin:$PATH

COPY .env.docker /app/.env.docker
COPY entrypoint_celery.py /app/entrypoint_celery.py
COPY entrypoint_docker.sh /app/entrypoint_docker.sh
COPY *_secret.json /app/
COPY app.py /app/app.py
COPY ./print_api/ /app/print_api/

RUN chmod +x /app/entrypoint_docker.sh
USER iforger
EXPOSE 5000
CMD ["./entrypoint_docker.sh"]