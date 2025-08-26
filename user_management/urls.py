# user_management/urls.py
from django.urls import path
from .views import LoginView ,LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
     path('logout/', LogoutView.as_view(), name='logout'),
 
    # path('otp-login/', OTPLoginView.as_view(), name='otp-login'),
]
