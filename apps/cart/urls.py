from django.urls import path, re_path
from cart.views import CartAddView, CartInfoView

urlpatterns = [
    path('', CartInfoView.as_view(), name='show'),  # 购物车页面显示
    path('/add', CartAddView.as_view(), name='add'),  # 购物车记录添加
]
