#!/usr/bin/env bash
set -o errexit
pip install gunicorn django djangorestframework djangorestframework-simplejwt django-cors-headers psycopg2-binary python-decouple whitenoise dj-database-url
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate