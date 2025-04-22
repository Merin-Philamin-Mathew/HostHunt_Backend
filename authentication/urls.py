from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterUser.as_view(),name='register'),
    path('otp-verification/', VerifyOTP.as_view(),name='verify'),
    path('login/', LoginView.as_view(),name='login'),
    path('google-login/', GoogleLoginView.as_view(),name='google-login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(),name='token-refresh'),
    # path('api/token/owner/', CustomOwnerTokenView.as_view(), name='token_obtain_owner'),

    path('profile-details/', RegisterUser.as_view(),name='register'),
    path('identity-verification/', UploadIdentityVerification.as_view(),name='register'),
    path('profile/upload-pic/', UploadProfile.as_view(), name='upload_profile_pic'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),

]