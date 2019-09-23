from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template import loader, RequestContext
import os

# broker和worker在同一台机子上则需要加上本段代码
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django2_dailyfresh.settings')
django.setup()

from goods.models import *
from django_redis import get_redis_connection

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/0')


@app.task
def send_register_active_email(to_email, username, token):
    """define task func"""
    subject = '天天生鲜欢迎信息'
    message = ''
    html_message = '<h1>%s, 欢迎成为天天生鲜注册会员<h1>' \
                   '请点击下面链接激活账户<br/>' \
                   '<a href="http://127.0.0.1:8000/user/active/%s">' \
                   'http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message=message, from_email=sender, recipient_list=receiver, html_message=html_message)


@app.task
def generate_static_index_html():
    types = GoodsType.objects.all()
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')  # 轮播图
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')  # 促销活动信息

    for type in types:
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    # 加载模板文件
    temp = loader.get_template('static_index.html')
    static_index_html = temp.render(context)
    save_path = os.path.join(settings.BASE_DIR, 'static\\index.html')  # windows路径的问题
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(static_index_html)
