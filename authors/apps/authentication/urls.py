from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, AccountVerificationAPIView,
    SendEmailPasswordReset, ResetPassword, OauthAPIView, OauthlLoginAPIView
)
from authors.apps.profiles.views import (
    FollowGenericAPIView, FollowingListAPIView, FollowersListAPIView
)

urlpatterns = [
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
    path('auth/users/login', OauthlLoginAPIView.as_view(), name='oauth-login'),

    # follow: POST /api/users/<id>/follow
    # Unfollow: DELETE /api/users/<id>/follow
    path('users/<int:pk>/follow',
         FollowGenericAPIView.as_view()),

    # see followers GET /api/users/<id>/followers
    path('users/<int:pk>/followers',
         FollowersListAPIView.as_view()),

    # see users one is following GET /api/users/<id>/following
    path('users/<int:pk>/following',
         FollowingListAPIView.as_view())
]
