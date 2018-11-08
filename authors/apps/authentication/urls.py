from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, AccountVerificationAPIView,
    SendEmailPasswordReset, ResetPassword, OauthAPIView, OauthlLoginAPIView
)

urlpatterns = [
    # path('users/<pk>', UserRetrieveUpdateAPIView.as_view()),
    # Story not yet worked on
    path('users', RegistrationAPIView.as_view(), name='signup'),
    path('users/login', LoginAPIView.as_view(), name='login'),
    path('user/activate/<uidb64>/<activation_token>',
         AccountVerificationAPIView.as_view(), name='activate_account'),
    path('user/reset_password', SendEmailPasswordReset.as_view(),
         name='reset_password_email'),
    path('user/reset_password/<reset_password_token>', ResetPassword.as_view(),
         name='reset_password'),
    path('auth/<social_auth_Provider>', OauthAPIView.as_view(),
         name='oauth-singIn'),
    path('auth/users/login', OauthlLoginAPIView.as_view(), name='oauth-login')
]
