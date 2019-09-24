[![](https://img.shields.io/badge/ICU-996-blueviolet.svg)](https://github.com/Pad0y)
[![](https://img.shields.io/badge/language-python-red.svg)](https://github.com/Pad0y)
[![CSDN](https://img.shields.io/badge/CSDN-Pad0y-yellow.svg)](https://blog.csdn.net/qq_34356800)
---
# 天天生鲜-django2.2版本

## 简介
**本项目替换原项目框架django1.8为最新版的django2.2.5**，该项目包含了实际开发中的电商项目中大部分的功能开发和知识点实践，
是一个非常不错的django学习项目，同时也记录在替换框架中遇到的坑，所遇到的django1.x和2.x的区别，希望对各位有所帮助。

关键词：django2 celery fdfs haystack whoosh redis 高并发 电商

## 开发环境  
```text
python:3.6.5
django:2.2.5
pycharm:2019.2
OS: win10
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
![项目架构图](documents/mdImages/project_frame.png)

## 数据库表分析图
![数据库表分析图](documents/mdImages/db_design.png)


## 项目目录结构
```text
│  manage.py
│  mind.md
│  nginxConfig
│  README.md
│  requirements.txt
│  uwsgi
│  uwsgi2
│  __init__.py
│  
├─.idea
│  │  dailyfresh.iml
│  │  misc.xml
│  │  modules.xml
│  │  vcs.xml
│  │  workspace.xml
│  │  
│  └─inspectionProfiles
│          Project_Default.xml
│          
├─apps
│  │  __init__.py
│  │  
│  ├─cart
│  │  │  admin.py
│  │  │  models.py
│  │  │  tests.py
│  │  │  urls.py
│  │  │  views.py
│  │  │  __init__.py
│  │  │  
│  │  ├─migrations
│  │  │  │  __init__.py
│  │  │  │  
│  │  │  └─__pycache__
│  │  │          __init__.cpython-36.pyc
│  │  │          
│  │  └─__pycache__
│  │          admin.cpython-36.pyc
│  │          models.cpython-36.pyc
│  │          urls.cpython-36.pyc
│  │          __init__.cpython-36.pyc
│  │          
│  ├─goods
│  │  │  admin.py
│  │  │  models.py
│  │  │  search_indexes.py
│  │  │  tests.py
│  │  │  urls.py
│  │  │  views.py
│  │  │  __init__.py
│  │  │  
│  │  ├─migrations
│  │  │  │  0001_initial.py
│  │  │  │  __init__.py
│  │  │  │  
│  │  │  └─__pycache__
│  │  │          0001_initial.cpython-36.pyc
│  │  │          __init__.cpython-36.pyc
│  │  │          
│  │  └─__pycache__
│  │          admin.cpython-36.pyc
│  │          models.cpython-36.pyc
│  │          urls.cpython-36.pyc
│  │          views.cpython-36.pyc
│  │          __init__.cpython-36.pyc
│  │          
│  ├─order
│  │  │  admin.py
│  │  │  models.py
│  │  │  tests.py
│  │  │  urls.py
│  │  │  views.py
│  │  │  __init__.py
│  │  │  
│  │  ├─migrations
│  │  │  │  0001_initial.py
│  │  │  │  0002_auto_20181126_1609.py
│  │  │  │  __init__.py
│  │  │  │  
│  │  │  └─__pycache__
│  │  │          0001_initial.cpython-36.pyc
│  │  │          0002_auto_20181126_1609.cpython-36.pyc
│  │  │          __init__.cpython-36.pyc
│  │  │          
│  │  └─__pycache__
│  │          admin.cpython-36.pyc
│  │          models.cpython-36.pyc
│  │          urls.cpython-36.pyc
│  │          __init__.cpython-36.pyc
│  │          
│  └─user
│      │  admin.py
│      │  models.py
│      │  tests.py
│      │  urls.py
│      │  views.py
│      │  __init__.py
│      │  
│      ├─migrations
│      │  │  0001_initial.py
│      │  │  __init__.py
│      │  │  
│      │  └─__pycache__
│      │          0001_initial.cpython-36.pyc
│      │          __init__.cpython-36.pyc
│      │          
│      └─__pycache__
│              admin.cpython-36.pyc
│              models.cpython-36.pyc
│              urls.cpython-36.pyc
│              views.cpython-36.pyc
│              __init__.cpython-36.pyc
│              
├─celery_tasks
│  │  tasks.py
│  │  __init__.py
│  │  
│  └─__pycache__
│          tasks.cpython-36.pyc
│          __init__.cpython-36.pyc
│          
├─configurationFile
│  │  celeryDescript.md
│  │  fastDFSDownload.md
│  │  Full-textSearchEngine.md
│  │  nginxAndFastDFS-nginx-moduleDownload.md
│  │  redisDownload.md
│  │  virtualenvDescript.md
│  │  
│  ├─conf
│  │      client.conf
│  │      mod_fastdfs.conf
│  │      nginx.conf
│  │      redis.conf
│  │      search.png
│  │      storage.conf
│  │      tracker.conf
│  │      whoosh_cn_backend.py
│  │      
│  └─images
│          1.png
│          2.png
│          celery.png
│          celery_virtualenv.jpg
│          fehelper-github-com-yuanwenq-dailyfresh-blob-dev-dailyfresh-settings-py-1544797232546.png
│          p1_12.png
│          start_celery_conf.jpg
│          whoosh.png
│          
├─dailyfresh
│  │  settings.py
│  │  urls.py
│  │  wsgi.py
│  │  __init__.py
│  │  
│  └─__pycache__
│          settings.cpython-36.pyc
│          urls.cpython-36.pyc
│          wsgi.cpython-36.pyc
│          __init__.cpython-36.pyc
│          
├─db
│  │  base_model.py
│  │  __init__.py
│  │  
│  └─__pycache__
│          base_model.cpython-36.pyc
│          __init__.cpython-36.pyc
│          
├─static
│  │  cart.html
│  │  detail.html
│  │  index.html
│  │  list.html
│  │  login.html
│  │  place_order.html
│  │  register.html
│  │  user_center_info.html
│  │  user_center_order.html
│  │  user_center_site.html
│  │  
│  ├─css
│  │      main.css
│  │      reset.css
│  │      
│  ├─images
│  │  │  adv01.jpg
│  │  │  adv02.jpg
│  │  │  banner01.jpg
│  │  │  banner02.jpg
│  │  │  banner03.jpg
│  │  │  banner04.jpg
│  │  │  banner05.jpg
│  │  │  banner06.jpg
│  │  │  down.png
│  │  │  fruit.jpg
│  │  │  goods.jpg
│  │  │  goods02.jpg
│  │  │  goods_detail.jpg
│  │  │  icons.png
│  │  │  icons02.png
│  │  │  interval_line.png
│  │  │  left_bg.jpg
│  │  │  login_banner.png
│  │  │  logo.png
│  │  │  logo02.png
│  │  │  pay_icons.png
│  │  │  register_banner.png
│  │  │  shop_cart.png
│  │  │  slide.jpg
│  │  │  slide02.jpg
│  │  │  slide03.jpg
│  │  │  slide04.jpg
│  │  │  
│  │  └─goods
│  │          goods001.jpg
│  │          goods002.jpg
│  │          goods003.jpg
│  │          goods004.jpg
│  │          goods005.jpg
│  │          goods006.jpg
│  │          goods007.jpg
│  │          goods008.jpg
│  │          goods009.jpg
│  │          goods010.jpg
│  │          goods011.jpg
│  │          goods012.jpg
│  │          goods013.jpg
│  │          goods014.jpg
│  │          goods015.jpg
│  │          goods016.jpg
│  │          goods017.jpg
│  │          goods018.jpg
│  │          goods019.jpg
│  │          goods020.jpg
│  │          goods021.jpg
│  │          
│  └─js
│          jquery-1.12.4.min.js
│          jquery-ui.min.js
│          jquery.cookie.js
│          register.js
│          slide.js
│          
├─templates
│  │  base.html
│  │  base_detail_list.html
│  │  base_no_cart.html
│  │  base_user_center.html
│  │  cart.html
│  │  detail.html
│  │  index.html
│  │  list.html
│  │  login.html
│  │  order_comment.html
│  │  place_order.html
│  │  register.html
│  │  static_base.html
│  │  static_index.html
│  │  user_center_info.html
│  │  user_center_order.html
│  │  user_center_site.html
│  │  
│  └─search
│      │  search.html
│      │  search1.html
│      │  
│      └─indexes
│          └─goods
│                  goodssku_text.txt
│                  
└─utils
    │  mixin.py
    │  __init__.py
    │  
    └─fdfs
            client.conf
            storage.py
            __init__.py
```

celery4.x 不兼容win10系统的处理办法
- https://www.jianshu.com/p/57414db33c27 
- https://www.cnblogs.com/zipxzf/articles/11298180.html
```
```text
UnicodeEncodeError: 'gbk' codec can't encode character '\xa9' in position 3104: illegal multibyte sequence
with open(save_path, 'w',encoding='utf-8') as f:
```
TypeError at / 'bool' object is not callable
user.is_authenticated() ---> user.is_authenticated
https://www.jb51.net/article/167810.htm
```text
py3fdfs踩坑记录
https://www.jianshu.com/p/de789d6ea126
```

