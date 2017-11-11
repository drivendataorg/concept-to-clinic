#!/bin/bash
set -e

function postgres_ready(){
python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect("$DATABASE_URL")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."

python /app/manage.py migrate --settings=config.settings.production

/usr/local/bin/gunicorn config.wsgi -w 1 -b 0.0.0.0:$PORT --chdir=/app
