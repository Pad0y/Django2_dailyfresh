#!/bin/bash
/usr/sbin/nginx;
python3 manage.py collectstatic --noinput;
/usr/sbin/nginx -s reload;
python3 manage.py makemigrations;
python3 manage.py migrate;
python3 manage.py createcachetable;
uwsgi --ini uwsgi.ini;
celery -A celery_tasks.tasks worker --loglevel=info;
tail -100f /var/log/nginx/access.log;