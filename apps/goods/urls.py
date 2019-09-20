from django.urls import path
from goods.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),  # 首页
]
