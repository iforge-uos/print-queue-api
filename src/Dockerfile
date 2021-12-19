# The base image we want to inherit from
FROM python:latest
ENV PYTHONUNBUFFERED 1
ARG ENV=dev

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Expose the application on port 5000
EXPOSE 5000
# Run test server
CMD ["flask", "run", "--host", "0.0.0.0"]