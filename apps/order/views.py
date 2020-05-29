from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.views.generic import View
from django_redis import get_redis_connection
from user.models import Address
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from utils.mixin import LoginRequiredMixin
from datetime import datetime
from alipay import AliPay
import os


# /order/place
class OrderPlaceView(LoginRequiredMixin, View):
    """提交订单页面显示"""
    
    def post(self, request):
        """提交订单页面显示"""
        # 获取我们的登录用户
        user = request.user
        # 获取参数sku_ids
        sku_ids = request.POST.getlist('sku_ids')
        
        # 校验参数
        if not sku_ids:
            # cart page
            return redirect(reverse('cart:show'))
        
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        
        skus = []
        # 保存商品的总家属和总价
        total_count = 0
        total_price = 0
        # 便利sku_ids获取用户要购买的商品的信息
        for sku_id in sku_ids:
            # 根据商品的id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户要购买的商品的数量
            count = conn.hget(cart_key, sku_id)
            
            # bugfix redis显示问题
            count = count.decode()
            
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态给sku增加属性count,保存购买商品的数量
            sku.count = count
            # 动态给sku添加属性amount,保存购买商品的小计
            sku.amount = amount
            # 追加
            skus.append(sku)
            # 累加计算商品的总价和总剑术
            total_count += int(count)
            total_price += amount
        
        # 云飞： 世纪开发的时候，属于一个子系统
        transit_price = 10  # 写思
        
        # 是付款
        total_pay = total_price + transit_price
        
        # 获取用户的首见地址
        addrs = Address.objects.filter(user=user)
        
        # 组织上下文
        sku_ids = ','.join(sku_ids)  # [1, 25]->1, 25
        context = {'skus': skus,
                   'total_count': total_count,
                   'total_price': total_price,
                   'transit_price': transit_price,
                   'total_pay': total_pay,
                   'addrs': addrs,
                   'sku_ids': sku_ids}
        
        # 使用模板
        return render(request, 'place_order.html', context)


# 前端传递的参数: 地址的id 支付方法(pay_method), 用户要购买的商品id
# 悲观锁：执行的时候加琐 用户抢锁
class OrderCommitView(View):
    """订单创建"""
    
    # 事务装饰器
    @transaction.atomic
    def post(self, request):
        """订单创建"""
        # 判断用户是否登录,非后台无法使用LoginRequiredMixin验证
        user = request.user
        if not user.is_authenticated:
            # 用户美登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
        
        # 接受参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')
        
        # 校验参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
        
        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})
        
        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '地址不存在'})
        
        # 组织参数
        # 订单id： 年月日时间+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
        
        # 运费
        transit_price = 10
        
        # 总数木和总金额
        total_count = 0
        total_price = 0
        
        # 设置事务保存点
        save_id = transaction.savepoint()
        try:
            # 向df_order_info表中添加一条记录
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price)
            
            # 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            
            sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                # 获取商品的信息
                try:
                    # 悲观锁：select * from df_goods_sku where id=sku_id for update; for update 为加琐操作
                    sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                except:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'res': 4, 'errmsg': '商品不存在'})
                
                # 从redis中获取用户所要购买的商品的数量
                count = conn.hget(cart_key, sku_id)
                
                # 判断商品的库存
                if int(count) > sku.stock:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'res': 6, 'errmsg': ' 商品库存不足'})
                
                # 向df_order_goods表中添加一条记录
                OrderGoods.objects.create(order=order,
                                          sku=sku,
                                          count=count,
                                          price=sku.price)
                
                #  更新商品的库存和销量
                sku.stock -= int(count)
                sku.sales += int(count)
                sku.save()
                
                #  累加计算订单商品的总数量和总价格
                amount = sku.price * int(count)
                total_count += int(count)
                total_price += amount
            
            # 更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})
        
        # 提交事务
        transaction.savepoint_commit(save_id)
        conn.hdel(cart_key, *sku_ids)  # 拆包
        # 返回应答
        return JsonResponse({'res': 5, 'message': '创建成功'})


class OrderPayView(View):
    """订单支付"""
    
    def post(self, request):
        """订单支付"""
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
        
        # 接收参数
        order_id = request.POST.get('order_id')
        
        # 校验参数
        if not order_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
        
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})
        
        # app_private_key_string = open(os.path.join(settings.BASE_DIR, 'apps\\order\\app_private_key.pem')).read()
        # alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'apps\\order\\alipay_public_key.pem')).read()
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        # 业务处理：使用Python sdk调用支付宝的支付接口
        # 初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APP_ID,  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False True就会访问沙箱地址
        )
        
        # 调用支付接口
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        total_pay = order.total_price + order.transit_price  # Decimal格式
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单id
            total_amount=str(total_pay),
            subject='天天生鲜%s' % order_id,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )
        
        # 返回应答
        pay_url = settings.ALIPAY_GATEWAY_URL + order_string
        return JsonResponse({'res': 3, 'pay_url': pay_url})


# ajax post
# 前端传递参数 order_id
# /order/check
class CheckPayView(View):
    """查询订单支付结果"""
    
    def post(self, request):
        """查询支付结果"""
        # 用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登陆'})
        
        # 接收参数
        order_id = request.POST.get('order_id')
        
        # 校验参数
        if not order_id:
            print(order_id)
            return JsonResponse({'res': 1, 'errmsg': '无效的订单id'})
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
            print(order)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '订单错误'})
        
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        # 业务处理：使用Python sdk调用支付宝的支付接口
        # 初始化
        alipay = AliPay(
            appid="2016102200735309",  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False True就会访问沙箱地址
        )
        
        # 调用支付宝交易查询接口
        while True:
            response = alipay.api_alipay_trade_query(order_id)
            
            """
                响应参数
                response = {              
                    "trade_no": "2019092121001004070200176844", # 支付宝交易号
                    "code": "10000", # 接口调用是否成功
                    "invoice_amount": "20.00",
                    "open_id": "20880072506750308812798160715407",
                    "fund_bill_list": [
                      {
                        "amount": "20.00",
                        "fund_channel": "ALIPAYACCOUNT"
                      }
                    ],
                    "buyer_logon_id": "csq***@sandbox.com",
                    "send_pay_date": "2019-09-21 13:29:17",
                    "receipt_amount": "20.00",
                    "out_trade_no": "out_trade_no15",
                    "buyer_pay_amount": "20.00",
                    "buyer_user_id": "2088102169481075",
                    "msg": "Success",
                    "point_amount": "0.00",
                    "trade_status": "TRADE_SUCCESS", # 支付结果
                    "total_amount": "20.00"
                }
             """
            
            code = response.get('code')
            
            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功
                # 获取支付宝交易号
                trade_no = response.get('trade_no')
                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 4  # 待评价状态
                order.save()
                # 返回结果
                return JsonResponse({'res': 3, 'message': '支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 等待卖家付款
                # 业务处理失败，可能一会就会成功
                import time
                time.sleep(5)
                continue
            else:
                # 支付出错
                return JsonResponse({'res': 4, 'errmsg': '支付失败'})


class CommentView(LoginRequiredMixin, View):
    """订单评论"""
    
    def get(self, request, order_id):
        """提供评论页面"""
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))
        
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))
        
        # 根据订单的状态获取订单的状态标题
        order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
        
        # 获取订单商品信息
        order_skus = OrderGoods.objects.filter(order_id=order_id)
        for order_sku in order_skus:
            # 计算商品的小计
            amount = order_sku.count * order_sku.price
            # 动态给order_sku增加属性amount,保存商品小计
            order_sku.amount = amount
        # 动态给order增加属性order_skus, 保存订单商品信息
        order.order_skus = order_skus
        
        # 使用模板
        return render(request, "order_comment.html", {"order": order})
    
    def post(self, request, order_id):
        """处理评论内容"""
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))
        
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))
        
        # 获取评论条数
        total_count = request.POST.get("total_count")
        total_count = int(total_count)
        
        # 循环获取订单中商品的评论内容
        for i in range(1, total_count + 1):
            # 获取评论的商品的id
            sku_id = request.POST.get("sku_%d" % i)  # sku_1 sku_2
            # 获取评论的商品的内容
            content = request.POST.get('content_%d' % i, '')  # cotent_1 content_2 content_3
            try:
                order_goods = OrderGoods.objects.get(order=order, sku_id=sku_id)
            except OrderGoods.DoesNotExist:
                continue
            
            order_goods.comment = content
            order_goods.save()
        
        order.order_status = 5  # 已完成
        order.save()
        
        return redirect(reverse("user:order", kwargs={"page": 1}))
