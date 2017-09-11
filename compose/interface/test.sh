#!/bin/sh
cd frontend && npm run build && cd ..
python manage.py test
