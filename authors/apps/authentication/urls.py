from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, AccountVerificationAPIView,
    SendEmailPasswordReset, ResetPassword, OauthAPIView, OauthlLoginAPIView,
    UnsubscribeNotifications, FacebookAPIView, GoogleAPIView, TwitterAPIView
)
from authors.apps.profiles.views import (
    FollowGenericAPIView, FollowingListAPIView, FollowersListAPIView
)

urlpatterns = [
    path('users', RegistrationAPIView.as_view(), name='signup'),
    path('users/<int:pk>/unsubscribe', UnsubscribeNotifications.as_view(),
         name='unsubscribe'),
    path('users/login', LoginAPIView.as_view(), name='login'),
    path('users/activate/<uidb64>/<activation_token>',
         AccountVerificationAPIView.as_view(), name='activate_account'),
    path('users/reset_password', SendEmailPasswordReset.as_view(),
         name='reset_password_email'),
    path('users/reset_password/<reset_password_token>',
         ResetPassword.as_view(),
         name='reset_password'),
    path('auth/<social_auth_Provider>', OauthAPIView.as_view(),
         name='oauth-singIn'),
    path('auth/users/login', OauthlLoginAPIView.as_view(), name='oauth-login'),
    path('auth/facebook/<str:access_token>', FacebookAPIView.as_view(),
         name='facebook-auth'),
    path('auth/google/<str:access_token>', GoogleAPIView.as_view(),
         name='google-auth'),

    path('auth/twitter/<str:access_key>/<str:access_secret>',
         TwitterAPIView.as_view(),
         name='twitter-auth'),

    # follow: POST /api/users/<id>/follow
    # Unfollow: DELETE /api/users/<id>/follow
    path('users/<str:username>/follow',
         FollowGenericAPIView.as_view()),

    # see followers GET /api/users/<id>/followers
    path('users/<str:username>/followers',
         FollowersListAPIView.as_view()),

    # see users one is following GET /api/users/<id>/following
    path('users/<str:username>/following',
         FollowingListAPIView.as_view())
]
