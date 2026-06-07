#!/usr/bin/env bash
set -o errexit
pip install gunicorn django djangorestframework djangorestframework-simplejwt django-cors-headers psycopg2-binary python-decouple whitenoise dj-database-url
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "
from users.models import CustomUser
if not CustomUser.objects.filter(email='admin@gmail.com').exists():
    CustomUser.objects.create_superuser(email='admin@gmail.com', name='Admin', phone='9999999999', password='admin1234')
    print('Superuser created')
else:
    print('Superuser already exists')
"