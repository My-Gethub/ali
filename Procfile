web: gunicorn STOR.wsgi
release: python manage.py migrate && python manage.py collectstatic --noinput
