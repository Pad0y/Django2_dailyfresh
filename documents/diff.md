# djang1.x 和 django2.x不同之处

## url和path的区别
- Django2.x中的path不支持正则匹配
但在同一目录下的re_path与Django1.x中的url功能大部分相同可以替代url。

```python
# django 2.x
from django.urls import path, re_path
--------------------------------------------------------------
# django1.x
from django.conf.urls import url
```
- 路由传参
```text
# django 2.x
urlpatterns = [
    path('order/<int:page>', UserOrderView.as_view(), name='order'),
]
------------------------------------------------------------------
# django 1.x
urlpatterns=[
    url(r'^order/(?P<page>[0-9]+)$',UserOrderView.as_view(), name='order')
]
```
- include()函数区别
```text
# 2.x 需要指定两个参数，第二个参数为所在的app名称，不然会报错
path('search/', include(('haystack.urls', 'haystack'))),
---------------------------------------------------------
url('search/', include('haystack.urls')),
```

# models部分
2.x指定外键必须添加on_delete参数
```python
models.ForeignKey('User', verbose_name='所属账户', on_delete=models.CASCADE)
```
# views部分
报错:TypeError at / 'bool' object is not callable

原因：is_authenticated 是属性而不是方法。

将
**if request.user.is_authenticated():** 

改为
if request.user.is_authenticated: