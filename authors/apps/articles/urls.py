from django.urls import path
from .views import (
    ArticlesListCreateAPIView,
    ArticleRetrieveByIdAPIView,
    ArticleRetrieveBySlugAPIView
)

urlpatterns = [
    # GET/POST api/articles
    path('', ArticlesListCreateAPIView.as_view(), name='list_create'),
    # GET api/articles/id
    path('/<int:pk>', ArticleRetrieveByIdAPIView.as_view(),
         name='article_by_id'),
    # GET api/articles/slug
    path('/<slug:slug>', ArticleRetrieveBySlugAPIView.as_view(),
         name='article_by_slug'),
]
