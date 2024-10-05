from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterUser.as_view(),name='register'),
    path('otp-verification/', VerifyOTP.as_view(),name='verify'),
    path('login/', LoginView.as_view(),name='login'),
    path('google-login/', GoogleLoginView.as_view(),name='google-login'),
]