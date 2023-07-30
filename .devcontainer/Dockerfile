FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd celery

EXPOSE 5000

CMD flask run --host=0.0.0.0 --port=5000 --reload
