from django.urls import path
from goods.views import IndexView, DetailView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),  # 首页
    path('index/', IndexView.as_view(), name='index'),  # 首页
    path('goods/<int:goods_id>', DetailView.as_view(), name='detail'),  # 详情页
]
