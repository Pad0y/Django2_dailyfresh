#!/usr/bin/env bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  bin="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$bin/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
bin="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

#source ~/.bash_profile
export LANG=en_US.UTF8
cd $bin

#/usr/bin/mkdir -p /etc/nginx/data/run
/usr/sbin/nginx

python3 manage.py collectstatic --noinput&&
python3 manage.py makemigrations&&
python3 manage.py migrate&&
python3 manage.py createcachetable&&
uwsgi --ini uwsgi.ini
