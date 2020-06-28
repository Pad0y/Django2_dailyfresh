# Author: Pad0y

FROM alpine:3.7

MAINTAINER Pad0y <1148364963@qq.com>

    # 定义变量
ENV HOME=/root/fastdfs \
    # nginx版本
    NGINX_VERSION=1.17.0 \
    # nginx端口默认值
    NGINX_PORT=8888 \
    # IP所在网络
    NET_VAR=eth0 \
    # fastdfs端口默认值
    FDFS_PORT=22122

# 创建目录并更换源
RUN mkdir -p ${HOME} && \
    echo -e "http://mirrors.aliyun.com/alpine/v3.7/main\nhttp://mirrors.aliyun.com/alpine/v3.7/community" > /etc/apk/repositories && \
    apk update

# 安装必要的软件
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

# 下载、安装libfastcommon
RUN cd ${HOME}/ \
    && curl -fSL  https://github.com/happyfish100/libfastcommon/archive/master.tar.gz -o fastcommon.tar.gz \
    && tar zxf fastcommon.tar.gz \
    && cd ${HOME}/libfastcommon-master/ \
    && ./make.sh \
    && ./make.sh install

# 下载、安装fastdfs
RUN cd ${HOME}/ \
    && curl -fSL  https://github.com/happyfish100/fastdfs/archive/master.tar.gz -o fastfs.tar.gz \
    && tar zxf fastfs.tar.gz \
    && cd ${HOME}/fastdfs-master/ \
    && ./make.sh \
    && ./make.sh install

# 配置fastdfs
RUN cd /etc/fdfs/ \
    && cp storage.conf.sample storage.conf \
    && sed -i "s|/home/yuqing/fastdfs|/var/local/fdfs/storage|g" /etc/fdfs/storage.conf \
    && cp tracker.conf.sample tracker.conf \
    && sed -i "s|/home/yuqing/fastdfs|/var/local/fdfs/tracker|g" /etc/fdfs/tracker.conf \
    && cp client.conf.sample client.conf \
    && sed -i "s|/home/yuqing/fastdfs|/var/local/fdfs/storage|g" /etc/fdfs/client.conf 

# 下载nginx插件
RUN cd ${HOME}/ \
    && curl -fSL  https://github.com/happyfish100/fastdfs-nginx-module/archive/master.tar.gz -o nginx-module.tar.gz \
    && tar zxf nginx-module.tar.gz

# 下载nginx
RUN cd ${HOME}/ \
    && curl -fSL http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz -o nginx-${NGINX_VERSION}.tar.gz \
    && tar zxf nginx-${NGINX_VERSION}.tar.gz

# 修复编译找不到 #include "common_define.h"的致命问题
# ADD ./config ${HOME}/fastdfs-nginx-module-master/src

# 将nginx和fastdfs的nginx插件编译
RUN cd ${HOME} \
    && chmod u+x ${HOME}/fastdfs-nginx-module-master/src/config \
    && cd nginx-${NGINX_VERSION} \
    && ./configure --add-module=${HOME}/fastdfs-nginx-module-master/src \
    && make && make install

# 配置nginx和fastdfs环境，配置nginx
RUN cp ${HOME}/fastdfs-nginx-module-master/src/mod_fastdfs.conf /etc/fdfs/ \
    && sed -i "s|^store_path0.*$|store_path0=/var/local/fdfs/storage|g" /etc/fdfs/mod_fastdfs.conf \
    && sed -i "s|^url_have_group_name=.*$|url_have_group_name=true|g" /etc/fdfs/mod_fastdfs.conf \
    && cd ${HOME}/fastdfs-master/conf/ \
    && cp http.conf mime.types anti-steal.jpg /etc/fdfs/ \
    && echo -e "events {\n\
    worker_connections  1024;\n\
}\n\
http {\n\
    include       mime.types;\n\
    default_type  application/octet-stream;\n\
    server {\n\
        listen \$NGINX_PORT;\n\
        server_name localhost;\n\
        location ~ /group[0-9]/M00 {\n\
            ngx_fastdfs_module;\n\
        }\n\
    }\n\
}">/usr/local/nginx/conf/nginx.conf

# 清理临时软件和文件
RUN rm -rf ${HOME}/*
RUN apk del .mybuilds
RUN apk add bash pcre-dev zlib-dev

# 创建启动脚本
RUN echo -e "mkdir -p /var/local/fdfs/storage/data /var/local/fdfs/tracker; \n\
ln -s /var/local/fdfs/storage/data/ /var/local/fdfs/storage/data/M00; \n\n\
sed -i \"s/listen\ .*$/listen\ \$NGINX_PORT;/g\" /usr/local/nginx/conf/nginx.conf; \n\
sed -i \"s/http.server_port=.*$/http.server_port=\$NGINX_PORT/g\" /etc/fdfs/storage.conf; \n\
if [ \"\$HOST_IP\" = \"\" ]; then \n\
    HOST_IP=\$(ifconfig \$NET_VAR | grep \"inet\" | grep -v \"inet6\" | awk '{print \$2}' | awk -F: '{print \$2}')\n\
fi \n\
sed -i \"s/^tracker_server=.*$/tracker_server=\$HOST_IP:\$FDFS_PORT/g\" /etc/fdfs/storage.conf; \n\
sed -i \"s/^tracker_server=.*$/tracker_server=\$HOST_IP:\$FDFS_PORT/g\" /etc/fdfs/client.conf; \n\
sed -i \"s/^tracker_server=.*$/tracker_server=\$HOST_IP:\$FDFS_PORT/g\" /etc/fdfs/mod_fastdfs.conf; \n\
/etc/init.d/fdfs_trackerd start; \n\
/etc/init.d/fdfs_storaged start; \n\
/usr/local/nginx/sbin/nginx; \n\
tail -f /usr/local/nginx/logs/access.log \
">/start.sh \
&& chmod u+x /start.sh

# 暴露端口
EXPOSE ${NGINX_PORT} ${FDFS_PORT}

ENTRYPOINT ["/bin/bash","/start.sh"]
