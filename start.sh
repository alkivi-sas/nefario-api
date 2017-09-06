#!/bin/bash

# Variables from environement
# WEB_SERVER : gunicorn or flask (for debug)
: "${MODE:=main}"
: "${WEB_SERVER:=gunicorn}"
: "${HOST:=0.0.0.0}"

if [ "${MODE}" == "main" ]; then
    python /manage.py createdb
    if [ "${WEB_SERVER}" == "gunicorn" ]; then
        while sleep 1; do gunicorn -b ${HOST}:5000 -k eventlet -w 1 nefario.wsgi; done;
    else
        while sleep 1; do python /manage.py runserver -h ${HOST}; done;
    fi
elif [ "${MODE}" == "worker" ]; then
    export C_FORCE_ROOT=TRUE
    while sleep 2; do celery worker -l debug -A nefario.celery; done;
fi
