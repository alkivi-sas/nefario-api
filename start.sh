#!/bin/sh
python /manage.py createdb
while sleep 5; do python /manage.py runserver -h 0.0.0.0; done;
