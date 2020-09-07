FROM ubuntu:18.04
LABEL author="Pad0y" github="github.com/pad0y"

ENV HOME=/root \
    PACKAGEPATH = /usr/local/lib/python3.6/dist-packages \
    NGINX_VERSION=1.17.0


WORKDIR /data/project
COPY . .
# update source.list and timezone
RUN echo -e "deb http://mirrors.tencentyun.com/ubuntu/ bionic main restricted universe multiverse\n\
deb http://mirrors.tencentyun.com/ubuntu/ bionic-security main restricted universe multiverse\n\
deb http://mirrors.tencentyun.com/ubuntu/ bionic-updates main restricted universe multiverse\n\
deb-src http://mirrors.tencentyun.com/ubuntu/ bionic main restricted universe multiverse\n\
deb-src http://mirrors.tencentyun.com/ubuntu/ bionic-security main restricted universe multiverse\n\
deb-src http://mirrors.tencentyun.com/ubuntu/ bionic-updates main restricted universe multiverse"\
        > /etc/apt/sources.list && apt update

RUN cd ./resource \
    && tar zxvf sqlite-autoconf-3300100.tar.gz \
    && cd sqlite-autoconf-3300100 && ./configure --prefix=/usr/local \
    && make && make install && make clean \
    && mv /usr/bin/sqlite3  /usr/bin/sqlite3_old \
    && ln -s /usr/local/bin/sqlite3   /usr/bin/sqlite3 \
    && echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite3.conf

RUN apt install -y python3-dev python3-pip libmysqlclient-dev\
    && python3 -m pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    && python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

RUN python3 -m pip install -r requirements.txt \
    && cp resource/ChineseAnalyzer.py resource/whoosh_cn_backend.py ${PACKAGEPATH}/haystack/backends/

RUN cd ${HOME}/ \
    && curl -fSL http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz -o nginx-${NGINX_VERSION}.tar.gz \
    && tar zxf nginx-${NGINX_VERSION}.tar.gz \
    && cd nginx-${NGINX_VERSION} \
    && chmod u+x ${HOME}/fastdfs-nginx-module-master/src/config \
    && ./configure --add-module=${HOME}/fastdfs-nginx-module-master/src \
    && make && make install && make clean


RUN rm -rf ${HOME}/.cache/pip/* \
    && rm -rf /var/cache/* \
    && rm -rf ${HOME}/*

ENTRYPOINT ["/bin/bash", "start.sh"]