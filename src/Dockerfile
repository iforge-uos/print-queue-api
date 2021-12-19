# The base image we want to inherit from
FROM python:latest
ENV PYTHONUNBUFFERED 1
ARG ENV=dev

ADD . /src
WORKDIR /src


RUN pip install -r requirements.txt


# Expose the application on port 8000
EXPOSE 5000
# Run test server
CMD python app.py