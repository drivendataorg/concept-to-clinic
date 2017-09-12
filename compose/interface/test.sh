#!/bin/sh
cd /app/frontend && npm install && npm run build && cd /app
python manage.py test
