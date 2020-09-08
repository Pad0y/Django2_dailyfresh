FROM ubuntu:18.04
LABEL author="Pad0y" github="github.com/pad0y"

ENV HOME=/root \
#    PACKAGEPATH = /usr/local/lib/python3.6/dist-packages \
    NGINX_VERSION=1.17.0


WORKDIR /data/project
COPY . .

# update source.list and timezone
#RUN echo -e "deb http://mirrors.tencentyun.com/ubuntu/ bionic main restricted universe multiverse\n\
#deb http://mirrors.tencentyun.com/ubuntu/ bionic-security main restricted universe multiverse\n\
#deb http://mirrors.tencentyun.com/ubuntu/ bionic-updates main restricted universe multiverse\n\
#deb-src http://mirrors.tencentyun.com/ubuntu/ bionic main restricted universe multiverse\n\
#deb-src http://mirrors.tencentyun.com/ubuntu/ bionic-security main restricted universe multiverse\n\
#deb-src http://mirrors.tencentyun.com/ubuntu/ bionic-updates main restricted universe multiverse"\
#        > /etc/apt/sources.list && apt-get update
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && apt-get update

RUN apt-get install -y python3-dev python3-pip libmysqlclient-dev curl nginx gcc g++ \
    openssl libssl-dev libpcre3 libpcre3-dev zlib1g-dev build-essential libtool \
#    && apt-get --fix-missing \
    && python3 -m pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    && python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# update sqlite3
RUN cd resource \
    && tar zxvf sqlite-autoconf-3300100.tar.gz \
    && cd sqlite-autoconf-3300100 && ./configure --prefix=/usr/local \
    && make && make install && make clean \
    && ln -s /usr/local/bin/sqlite3   /usr/bin/sqlite3 \
    && echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite3.conf \
    && ldconfig

# install project packages
RUN python3 -m pip install -r requirements.txt \
    && cp resource/ChineseAnalyzer.py resource/whoosh_cn_backend.py /usr/local/lib/python3.6/dist-packages/haystack/backends/

RUN cp compose/nginx.conf /etc/nginx \
    && cp ./compose/default.conf /etc/nginx/conf.d \
    && chmod +x start.sh


# clean up cache to
#RUN apt-get remove -y --auto-remove curl gcc g++ \
#    && rm -rf ${HOME}/.cache/pip/* \
#    && rm -rf /var/cache/* \
#    && rm -rf ${HOME}/*

RUN apt-get remove -y --auto-remove curl gcc g++ \
RUN rm -rf ${HOME}/.cache/pip/* \
RUN rm -rf /var/cache/* && rm -rf ${HOME}/*

ENTRYPOINT ["/bin/bash", "start.sh"]
CMD ["/bin/bash"]