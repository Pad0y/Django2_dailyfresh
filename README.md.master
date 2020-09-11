[![](https://img.shields.io/badge/ICU-996-blueviolet.svg)](https://github.com/Pad0y)
[![](https://img.shields.io/badge/language-python-red.svg)](https://github.com/Pad0y)
[![CSDN](https://img.shields.io/badge/CSDN-Pad0y-yellow.svg)](https://blog.csdn.net/qq_34356800)
[![Build Status](https://www.travis-ci.org/Pad0y/Django2_dailyfresh.svg?branch=master)](https://www.travis-ci.org/Pad0y/Django2_dailyfresh)
![Finish](https://img.shields.io/badge/Finish-true-green)
---
# 天天生鲜-django2.2版本

## 简介
**本项目替换原项目框架django1.8为最新版的django2.2.5（已修复为2.2.10）**，该项目包含了实际开发中的电商项目中大部分的功能开发和知识点实践，
是一个非常不错的django学习项目，同时也记录在替换框架中遇到的坑，所遇到的django1.x和2.x的区别，希望对各位的学习有所帮助。

关键词：django2 celery fdfs haystack whoosh redis nginx 高并发 分布式

# 主要技术栈
```text
celery：分别负责用户注册异步发送邮件以及不同用户登陆系统动态生成首页
fdfs+nginx：存储网站静态文件，实现项目和资源分离，达到分布式效果
haystack+whoosh+jieba：全文检索框架，修改底层haystack库使之对中文搜索更加友好
redis：作为django缓存和session存储后端，提升网站性能，给予用户更好体验
```
## 开发环境  
```text
python:3.6.5
django:2.2.10
pycharm:2019.2
OS: windows 10
```
## 功能模块
- [x] 用户模块
    - [x] 注册
    - [x] 登录
    - [x] 激活(celery)
    - [x] 退出
    - [x] 个人中心
    - [x] 地址管理
- [x] 商品模块
    - [x] 首页(celery)
    - [x] 商品详情
    - [x] 商品列表
    - [x] 搜索功能(haystack+whoosh)
- [x] 购物车模块(redis)
    - [x] 增加
    - [x] 删除
    - [x] 修改
    - [x] 查询
- [x] 订单模块
    - [x] 确认订单页面
    - [x] 订单创建
    - [x] 请求支付(支付宝)
    - [x] 查询支付结果
    - [x] 评论
 

## 项目架构图
![项目架构图](docs/mdImages/project_frame.png)

## 数据库表分析图
![数据库表分析图](docs/mdImages/db_design.png)

# 依赖环境和疑难解答
- [FDFS配合Nginx的安装](docs/FastDFS-description.md)
- [python3与fdfs交互踩坑记录](docs/py3fdfs.md)
- [windows上celery4.x不兼容问题完美解决办法](docs/celery_on_win10.md)
- [jieba分词设置修改](docs/jieba.md)
- [支付宝sdk接入](https://github.com/fzlee/alipay/blob/master/README.zh-hans.md)
- [django1.x和2.x的不同之处](docs/diff.md)

# 项目部署（开发环境）
- 依赖库安装
```text
pip install -U pip
pip install -r requirements.txt
```
- mysql数据库创建
```mysql
CREATE DATABASE `dailyfresh` CHARACTER SET 'utf8mb4';
```
- 启动项目所需服务(win10)
```shell script
# windows redis的启动，配置文件在redis安装目录下
$ redis-server redis.windows.conf

# 启动celery, 进入项目虚拟环境，在项目根目录下执行
$ celery -A celery_tasks.tasks worker --loglevel=info -P eventlet
```

# 启动FastDFS服务, 启动nginx
fdfs的安装方式有两种：
- 1.[手动编译安装， 详见此处](docs/FastDFS-description.md)，
- 2.以docker方式运行

FDFS的安装配置是一件比较麻烦的事情，因此提供FDFS的Dockerfile，
首先把Dockerfile_FDFS 放到一个`空目录`中执行如下命令,不然会把项目一起打包到docker上
`docker build -t pad0y/fdfs:v3 -f FDFS.dockerfile .` 或者
[直接下载](https://hub.docker.com/r/pad0y/fdfs)
，自行构建还是直接拉镜像二选一即可。
```bash
docker pull pad0y/fdfs:v3
```
然后执行
```docker
# 当storage和tracker在同宿主机时，必须使用host模式，否则文件上传返回storage内部地址，外部访问无法使用
# MASTER_IP填写自己服务器的ip
docker run -d --name fdfs\
    -p 8888:8888 \
    -p 22122:22122 \
    -p 23000:23000 \
    -e TZ=Asia/Shanghai \
    -e NET_VAR=eth0 \
    -e MASTER_IP=YOUR SERVER IP\
    -v /mnt/fdfs:/var/local/fdfs \
    pad0y/fdfs:v3
```
修改`utils/fdfs/client_deploy.conf` tracker_server字段为自己服务器的ip

两种方法选择一种即可，建议docker搭建FDFS方便快捷！
FDFS环境准备好之后执行如下命令（本地环境安装），docker方式启动无需执行此步骤。
```shell script
$ /usr/bin/fdfs_trackerd /etc/fdfs/tracker.conf start
$ /usr/bin/fdfs_storaged /etc/fdfs/storage.conf start
$ nginx
```
# 项目配置文件修改
```text
1. 重命名Django2_dailyfresh文件夹下的settings.py.example
   文件为settings.py

2. 修改数据库配置信息
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'HOST': 'localhost',
        'PORT': '3306',
        'USER': '#',  # 数据库用户名
        'PASSWORD': '#',  # 数据库密码
    }
}

3. 修改邮箱配置信息，163邮箱配置信息自查
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'xxxx@qq.com'  # 发送邮件的邮箱
EMAIL_HOST_PASSWORD = 'xxxx'  # qq邮箱授权码
# EMAIL_USE_TLS = True  # 与SMTP服务器通信时，是否启动TLS链接(安全链接)
EMAIL_FROM = '天天生鲜<XXXXX@qq.com>'  # EMAIL_FROM 和 EMAIL_HOST_USER必须一样

4. 填写fdfs的配置信息，注意端口是nginx的端口
FDFS_STORAGE_URL = 'http://ip:port/'  

5. 支付功能不需要用到的保持默认即可，需要用到移步官方文档或看配置文件注释
```
# 迁移数据库
```
python manage.py makemigrations
python manage.py migrate
```
# 启动
```
# 创建超级管理员
python manage.py createsuperuser
# 缓存表
python manage.py createcachetable
# 启动服务
python manage.py runserver
```
# 效果图
![首页效果图](docs/mdImages/index.png)
![首页效果图](docs/mdImages/index2.png)
![后台显示](docs/mdImages/backend-display.png)
# BUGFIX
- 2020.6.06: [Bump django from 2.2.10 to 2.2.13](https://github.com/Pad0y/Django2_dailyfresh/pull/8)
- 2020.4.12: Fixed the background management page display
- 2020.4.02: [Fixed CVE-2020-5313 FLI buffer overflow](https://github.com/advisories/GHSA-hj69-c76v-86wr)
- 2020.2.12：[Fixed CVE-2020-7471 SQL injection](https://www.djangoproject.com/weblog/2020/feb/03/security-releases/)
- 2020.1.17：[Fixed CVE-2019-19844](https://github.com/advisories/GHSA-vfq6-hq5r-27r6)
- 2019.11.6：[Fixed CVE-2019-19118](https://github.com/advisories/GHSA-hvmf-r92r-27hr)
- 2019.10.23：[Bump pillow from 6.1.0 to 6.2.0 ](https://github.com/Pad0y/Django2_dailyfresh/pull/3/commits/f2c74ed0a8d262b1da722dfdb4815348ec31992e)

# 后言
如果本项目能帮助到在学习django2的你或者对你有其他帮助记得给个star噢!:wink:
若有什么需要改进或者疑问的地方欢迎提出issue 
