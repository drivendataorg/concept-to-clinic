#!/bin/sh
python /app/manage.py migrate --settings=config.settings.production
/usr/local/bin/gunicorn config.wsgi -w 1 -b 0.0.0.0:$PORT --chdir=/app
