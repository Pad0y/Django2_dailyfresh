from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate, login
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from user.models import User
from celery_tasks.tasks import send_register_active_email
import re


# /user/register.html
# def register(request):
#     """注册"""
#     if request.method == 'GET':
#         # 显示注册页面
#         return render(request, 'register.html')
#     else:
#         # 接受数据
#         username = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#         # 数据校验
#         if not all([username, password, email]):
#             # 数据不完整
#             return render(request, 'register.html', {'errmsg': '用户信息不完整'})
#
#         if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
#             # 邮箱格式不正确
#             return render(request, 'register.html', {'errmsg': '邮箱不合法'})
#
#         if allow != 'on':
#             # 是否同意协议
#             return render(request, 'register.html', {'errmsg': '请同意协议'})
#
#         # 校验用户名是否重复
#         try:
#             User.objects.get(username=username)
#         except User.DoesNotExist:
#             User.username = None
#
#         if User.username:
#             # 用户名存在
#             return render(request, 'register.html', {'errmsg': '用户名已存在'})
#
#         # 进行业务处理：进行注册,django内置的用户认证系统
#         user = User.objects.create_user(username, email, password)
#         user.is_active = 0  # 禁止激活
#         user.save()
#
#         # 返回应答,跳转到index
#         return redirect(reverse('goods:index'))


class RegisterView(View):
    """注册类视图"""

    def get(self, request):
        """显示注册页面"""
        return render(request, 'register.html')

    def post(self, request):
        """进行注册处理"""
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '用户信息不完整'})

        if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            # 邮箱格式不正确
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})

        if allow != 'on':
            # 是否同意协议
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            User.username = None

        if User.username:
            # 用户名存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理：进行注册,django内置的用户认证系统
        user = User.objects.create_user(username, email, password)
        user.is_active = 0  # 禁止激活
        user.save()

        # 发送激活邮件，包含激活链接 /user/active/id
        # 加密用户的身份信息,生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode('utf8')

        # 异步发送邮件
        send_register_active_email.delay(email, username, token)
        # 返回应答,跳转到index
        return redirect(reverse('goods:index'))


class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        # 解密参数
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']

            # 根据id获取用户id
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转登录
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


# /user/login
class LoginView(View):
    def get(self, request):
        """显示登录页面"""
        return render(request, 'login.html')

    def post(self, request):
        """登录校验"""

        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 业务处理
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # 记录登陆状态 session
                login(request, user)
                return redirect(reverse('goods:index'))

            else:
                return render(request, 'login.html', {'errmsg': '账户未激活'})

        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
