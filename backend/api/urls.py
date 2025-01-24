from django.urls import path
from .views import (SignupView, VerifyOTPView, ResendOtpAPIView,
                    LoginView,ResetPasswordView,RequestPasswordResetView,
                    LoginWithGoogle,UserProfileView)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOtpAPIView.as_view(), name='resend_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('request-reset-password/', RequestPasswordResetView.as_view(), name='request-reset-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('login-with-google/',LoginWithGoogle.as_view(),name='login-with-google'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
