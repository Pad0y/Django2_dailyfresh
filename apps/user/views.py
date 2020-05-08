from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired

from order.models import OrderInfo, OrderGoods
from user.models import User, Address
from goods.models import GoodsSKU
from celery_tasks.tasks import send_register_active_email
from utils.mixin import LoginRequiredMixin
import re


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
        # 判断是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

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

                # 获取登陆后要跳转的地址, 默认跳转首页
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)  # HttpResponseRedirect

                # 判断是否记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username', username, max_age=24 * 3600)
                else:
                    response.delete_cookie(username)
                return response
            else:
                return render(request, 'login.html', {'errmsg': '账户未激活'})

        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


# /user/logout
class LogoutView(View):
    def get(self, request):
        """退出登录"""
        # 清除用户session
        logout(request)
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页"""

    def get(self, request):
        # django会把request.user传给模板

        # 获取用户个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户浏览历史
        con = get_redis_connection('default')  # StrictRedis对象
        history_key = 'history_%d' % user.id
        # 获取最新五条浏览记录
        sku_ids = con.lrange(history_key, 0, 4)
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文
        context = {
            'page': 'user',
            'address': address,
            'goods_li': goods_li
        }
        return render(request, 'user_center_info.html', context)


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    """用户中心-信息页"""

    def get(self, request, page):
        """显示"""
        # 获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 便利获取订单商品的信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            # 便利order_skus计算商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性amount，保存订单商品的小计
                order_sku.amount = amount
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 动态给order增加属性，保存订单商品的信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        print(order_page)
        # 组织上下文
        context = {'order_page': order_page,
                   'pages': pages,
                   'page': 'order'}

        return render(request, 'user_center_order.html', context)


# /user/address
class AddressView(LoginRequiredMixin, View):
    """用户中心-地址页"""

    def get(self, request):
        # 获取用户地址
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        # address = Address.objects.get_default_address(user)
        # return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

        default_address = Address.objects.get_default_address(user)

        all_address = Address.objects.get_all_address(user)

        # 组织模板上下文
        context = {
            'address': default_address,
            'have_address': all_address,
            'page': 'address'
        }

        # 使用模板
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        """地址添加"""
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 手机号校验
        if not re.match(r'1[3,4,5,7,8]\d{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        if len(zip_code) != 6:
            return render(request, 'user_center_site.html', {'errmsg': '邮件编码错误'})

        # 业务添加:如果用户已存在默认收货地址，添加的地址不作为默认地址，否则作为默认
        user = request.user
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        return redirect(reverse('user:address'))
