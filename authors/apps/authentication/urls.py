from django.urls import path, re_path

from .views import (
    LoginAPIView, RegistrationAPIView, AccountVerificationAPIView,
    SendEmailPasswordReset, ResetPassword
)

urlpatterns = [
    # path('users/<pk>', UserRetrieveUpdateAPIView.as_view()), Story not yet worked on
    path('users', RegistrationAPIView.as_view(), name='signup'),
    path('users/login', LoginAPIView.as_view(), name='login'),
    path('user/activate/<uidb64>/<activation_token>',
         AccountVerificationAPIView.as_view(), name='activate_account'),
    path('user/reset_password', SendEmailPasswordReset.as_view(),
         name='reset_password_email'),
    path('user/reset_password/<reset_password_token>', ResetPassword.as_view(),
         name='reset_password')
]
