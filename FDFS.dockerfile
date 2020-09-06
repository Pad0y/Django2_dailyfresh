FROM alpine:3.7

LABEL author="Pad0y" github="github.com/pad0y"

# set env
ENV HOME=/root \
    NGINX_VERSION=1.17.0 \
    NGINX_PORT=8888 \
    NET_VAR=eth0 \
    FDFS_PORT=22122 \
    MASTER_IP=0.0.0.0

# update repositories
RUN mkdir -p ${HOME} && \
    echo -e "http://mirrors.aliyun.com/alpine/v3.7/main\nhttp://mirrors.aliyun.com/alpine/v3.7/community">/etc/apk/repositories && \
    apk update

# download dependency library
RUN apk add --no-cache --virtual .mybuilds \
    bash \
    gcc \
    make \
    linux-headers \
    curl \
    gnupg \
    gd-dev \
    pcre-dev \
    zlib-dev \
    libc-dev \
    libxslt-dev \
    openssl-dev \
    geoip-dev

# download and install fastcommon
RUN cd ${HOME}/ \
    && curl -fSL https://github.com/happyfish100/libfastcommon/archive/master.tar.gz -o fastcommon.tar.gz \
    && tar zxf fastcommon.tar.gz \
    && cd ${HOME}/libfastcommon-master/ \
    && ./make.sh \
    && ./make.sh install

# download and install fastdfs
RUN cd ${HOME}/ \
    && curl -fSL https://github.com/happyfish100/fastdfs/archive/master.tar.gz -o fastfs.tar.gz \
    && tar zxf fastfs.tar.gz \
    && cd ${HOME}/fastdfs-master/ \
    && ./make.sh \
    && ./make.sh install

# download fastdfs-nginx-module
RUN cd ${HOME}/ \
    && curl -fSL  https://github.com/happyfish100/fastdfs-nginx-module/archive/master.tar.gz -o nginx-module.tar.gz \
    && tar zxf nginx-module.tar.gz \
    && cd fastdfs-nginx-module-master/src \
    && sed -i "s|ngx_module_incs=.*$|ngx_module_incs=\"/usr/include/fastdfs /usr/include/fastcommon/\"|g" ./config \
    && sed -i "s|CORE_INCS=.*$|CORE_INCS=\"\$CORE_INCS /usr/include/fastdfs /usr/include/fastcommon/\"|g" ./config

# download nginx
RUN cd ${HOME}/ \
    && curl -fSL http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz -o nginx-${NGINX_VERSION}.tar.gz \
    && tar zxf nginx-${NGINX_VERSION}.tar.gz \
    && cd nginx-${NGINX_VERSION} \
    && chmod u+x ${HOME}/fastdfs-nginx-module-master/src/config \
    && ./configure --add-module=${HOME}/fastdfs-nginx-module-master/src \
    && make && make install && make clean


# configure FDFS base_dir
RUN cd /etc/fdfs/ \
    && cp ${HOME}/fastdfs-master/conf/* /etc/fdfs/ \
    && IP=$(ifconfig eth0 |grep inet|awk '{print $2}'|tr -d "addr:") \
    && sed -i "s|/home/yuqing/fastdfs|/var/local/fdfs/storage|g" /etc/fdfs/storage.conf \
    && sed -i "s|/home/yuqing/fastdfs|/var/local/fdfs/tracker|g" /etc/fdfs/tracker.conf \
    && sed -i "s|/home/yuqing/fastdfs|/var/local/fdfs/storage|g" /etc/fdfs/client.conf \
    && sed -i "s|^http.tracker_server_port =.*$|http.tracker_server_port = $(cat tracker.conf|grep http.server_port|awk '{print $3}')|g" /etc/fdfs/client.conf

# configure fastdfs-nginx-module
RUN cp ${HOME}/fastdfs-nginx-module-master/src/mod_fastdfs.conf /etc/fdfs/ \
    && sed -i "s|^store_path0.*$|store_path0=/var/local/fdfs/storage|g" /etc/fdfs/mod_fastdfs.conf \
    && sed -i "s|^url_have_group_name\s*=\s*.*$|url_have_group_name = true|g"  /etc/fdfs/mod_fastdfs.conf \
    && echo -e "events {\n\
    worker_connections  1024;\n\
}\n\
http {\n\
    include       mime.types;\n\
    default_type  application/octet-stream;\n\
    server {\n\
        listen $NGINX_PORT;\n\
        server_name localhost;\n\
        location ~ /group[0-9]/M00 {\n\
            root /var/local/fdfs/storage/data;\n\
            ngx_fastdfs_module;\n\
        }\n\
    }\n\
}">/usr/local/nginx/conf/nginx.conf

# clean up temp and unuseless softwares
RUN rm -rf ${HOME}/*
RUN apk del .mybuilds
RUN apk add bash pcre-dev zlib-dev

# create start.sh shell script
RUN echo -e "mkdir -p /var/local/fdfs/storage/data /var/local/fdfs/tracker; \n\
ln -s /var/local/fdfs/storage/data/ /var/local/fdfs/storage/data/M00; \n\n\
#sed -i \"s/listen\ .*$/listen\ \$NGINX_PORT;/g\" /usr/local/nginx/conf/nginx.conf; \n\
sed -i \"s/http.server_port = .*$/http.server_port = \$NGINX_PORT/g\" /etc/fdfs/storage.conf; \n\
HOST_IP=\$(ifconfig \$NET_VAR | grep \"inet\" | awk '{print \$2}' | tr -d \"addr:\")\n\
sed -i \"s/^tracker_server =.*$/tracker_server = \$MASTER_IP:\$FDFS_PORT/g\" /etc/fdfs/storage.conf; \n\
sed -i \"s/^tracker_server =.*$/tracker_server = \$MASTER_IP:\$FDFS_PORT/g\" /etc/fdfs/client.conf; \n\
sed -i \"s/^tracker_server=.*$/tracker_server=\$MASTER_IP:\$FDFS_PORT/g\" /etc/fdfs/mod_fastdfs.conf; \n\
/etc/init.d/fdfs_trackerd start; \n\
/etc/init.d/fdfs_storaged start; \n\
/usr/local/nginx/sbin/nginx; \n\
tail -f /usr/local/nginx/logs/access.log">/start.sh \
&& chmod u+x /start.sh

# expose ports
EXPOSE ${NGINX_PORT} ${FDFS_PORT} 23000 8080

ENTRYPOINT ["/bin/bash","/start.sh"]
