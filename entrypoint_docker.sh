#!/bin/sh

flask one-time-db
exec gunicorn -w 4 -b :5000 app:app
