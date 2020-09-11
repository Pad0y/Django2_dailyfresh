#!/bin/bash

#set -o errexit
#set -o pipefail
#
#
#
#function mysql_ready(){
#python3 << END
#import sys
#import pymysql
#try:
#    conn = pymysql.connect(host="db", port=3306, user="root", passwd="$MYSQL_ROOT_PASSWORD", db='$MYSQL_DATABASE', charset='utf8')
#except pymysql.err.OperationalError:
#    sys.exit(-1)
#sys.exit(0)
#END
#}
#
#until mysql_ready; do
#  >&2 echo "MySQL is unavailable - sleeping"
#  sleep 1
#done
#
#>&2 echo "MySQL is up - continuing..."

/usr/sbin/nginx;
python3 manage.py collectstatic --noinput;
/usr/sbin/nginx -s reload;
python3 manage.py makemigrations;
python3 manage.py migrate;
python3 manage.py createcachetable;
uwsgi --ini uwsgi.ini;
tail -100f /var/log/nginx/access.log;