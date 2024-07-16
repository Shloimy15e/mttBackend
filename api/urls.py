from django.urls import path
from .views import UserLoginView
from .views import UserRegisterView
from .views import UserLogoutView

urlpatterns = [
    path('auth/register', UserRegisterView.as_view(), name='register'),
    path('auth/login', UserLoginView.as_view(), name='login'),
    path('auth/logout', UserLogoutView.as_view(), name='logout'),
]
