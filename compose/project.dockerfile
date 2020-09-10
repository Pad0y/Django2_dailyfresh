FROM ubuntu:18.04
#FROM pad0y/baseimage:v1
LABEL author="Pad0y" github="github.com/pad0y"

WORKDIR /data/project
COPY . .

RUN mkdir -p /data/config && mkdir -p /data/logs && mkdir -p /data/compose
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && sed -i '/security/d' /etc/apt/sources.list \
    && apt-get update

RUN apt-get install -y python3-dev python3-pip libmysqlclient-dev curl nginx gcc g++ sqlite3 \
    openssl libssl-dev libpcre3 libpcre3-dev zlib1g-dev build-essential libtool \
    && python3 -m pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
#    && python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
    && python3 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

# install project packages
RUN pip3 install -r requirements_global.txt
RUN pip3 install -r requirements.txt \
#    && tar zxvf resource/django-haystack-2.8.1.tar.gz && cd django-haystack-2.8.1 && python3 setup.py install \
    && cp resource/ChineseAnalyzer.py resource/whoosh_cn_backend.py /usr/local/lib/python3.6/dist-packages/haystack/backends/

RUN cp compose/nginx.conf /etc/nginx \
    && cp ./compose/default.conf /etc/nginx/conf.d \
    && chmod +x start.sh

#RUN mv /data/project/uwsgi.ini /data/project/Django2_dailyfresh/settings.py /data/project/utils/fdfs/client_deploy.conf \
#    /data/config/ && \
#    ln -s /data/config/uwsgi.ini ./uwsgi.ini && \
#    ln -s /data/config/settings.py ./Django2_dailyfresh/settings.py && \
#    ln -s /data/config/client.conf ./utils/fdfs/client_deploy.conf && \
#    ln -s /data/logs ./logs && \
#    ln -s /data/compose ./compose

# clean up cache
RUN apt-get remove -y --auto-remove curl gcc g++ \
    && rm -rf ${HOME}/.cache/pip/* \
    && rm -rf /var/cache/* \
    && rm -rf ${HOME}/* \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000 80

CMD ["/bin/bash", "start.sh"]
