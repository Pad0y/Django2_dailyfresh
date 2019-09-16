from django.urls import path
from goods import views

urlpatterns = [
    path('', views.index, name='index'),  # 首页
]
