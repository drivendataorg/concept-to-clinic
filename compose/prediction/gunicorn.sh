#!/bin/sh
/usr/local/bin/gunicorn src.factory:app -w 4 -b 0.0.0.0:5001 --chdir=/app -k gevent
