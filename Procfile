web: gunicorn authors.wsgi --log-file -
worker3: celery -A authors worker -l info
