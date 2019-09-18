from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView
from user import views

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    re_path('active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    path('login', LoginView.as_view(), name='login'),

    path('', UserInfoView.as_view(), name='user'),
    path('order', UserOrderView.as_view(), name='order'),
    path('address', AddressView.as_view(), name='address'),
]
