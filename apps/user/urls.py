from django.urls import path
from user.views import RegisterView
from user import views

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    # path('register', views.register, name='register'),
]
