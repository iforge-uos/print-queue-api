#!/bin/sh
flask nuke-db
exec gunicorn -w 4 -b :5000 app:app