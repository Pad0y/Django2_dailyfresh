from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import View

from user.models import User
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

        # 返回应答,跳转到index
        return redirect(reverse('goods:index'))
