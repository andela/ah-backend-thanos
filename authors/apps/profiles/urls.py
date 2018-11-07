from django.urls import path

from .views import (
    ProfileRetrieveUpdateAPIView,
    ProfileListAPIView
)

urlpatterns = [
    path('api/profiles/<username>',
         ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('api/profiles', ProfileListAPIView.as_view(), name='profile_list'),
]
