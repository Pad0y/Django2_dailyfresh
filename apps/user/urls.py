from django.urls import path,re_path
from user.views import RegisterView, ActiveView, LoginView
from user import views

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    re_path('active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    path('login', LoginView.as_view(), name='login'),
    # path('register', views.register, name='register'),
]
