[![](https://img.shields.io/badge/ICU-996-blueviolet.svg)](https://github.com/Pad0y)
[![](https://img.shields.io/badge/language-python-red.svg)](https://github.com/Pad0y)
[![Build Status](https://travis-ci.org/Pad0y/Mysite.svg?branch=master)](https://travis-ci.org/Pad0y/Mysite)
[![CSDN](https://img.shields.io/badge/CSDN-Pad0y-yellow.svg)](https://blog.csdn.net/qq_34356800)
---

# Environment:
```
- Python==3.6.5
- Django==2.1.5
- MySQL==5.7
```
# Installation
```
pip install -r requirments.txt
```
# Deploy on localhost
- **Migration and generate the database**
```
> git clone https://github.com/Pad0y/Mysite.git
> cd Mysite/
> python manage.py makemigrations
> python manage.py migrate
```
- **To create the cache table**
```
> python manage.py createcachetable
```

- **To create the administrator account**
```
> python manage.py createsuperuser
```
- **Start this project**
```
> python manage.py runserver [port] (default 8000)
```
```
and then open browser:127.0.0.1:8000/
the default Website backstage: 127.0.0.1:8000/admin/
```
---
*if you want to use other database,you can refer to the [url](https://docs.djangoproject.com/en/2.0/ref/settings/#databases)
and change the database configuration information in* **deployment.py**

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DATABASENAME',
        'USER': 'USERNAME',
        'PASSWORD': 'PASSWORD',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'YOUR EMAIL'  # 发送邮箱的邮箱地址
EMAIL_HOST_PASSWORD = 'Your authorization code'  # 授权码
EMAIL_SUBJECT_PREFIX = "[Pad0y's blog]"
EMAIL_USE_TLS = True  # 与SMTP服务器通信时，是否启动TLS链接(安全链接)

```
# Attentions!
```
The server and the local configuration file is different,
if you want to deploy the project to the server,
I suggest that make differents with two configuration files.
The sensitive information such as database password, secret key maybe written to the system environment variables.
If you want to let it run on your computer,just do the above!
and If there is doubt, please submit the issue to me!
```
# More configuration
```
If the project can help to you, give a start,
and your reply will be my motivation for continue update maintenance.

                                                                    Thanks！
```
