from django.urls import path
from .views import (
    ArticlesListCreateAPIView,
    ArticleRetrieveUpdateDestroy,
    ArticleRetrieveBySlugAPIView,
)

urlpatterns = [
    # GET/POST api/articles
    path('', ArticlesListCreateAPIView.as_view(), name='list_create'),

    # GET api/articles/id
    # PUT api/articles/id
    # DELETE api/articles/id
    path('/<int:pk>', ArticleRetrieveUpdateDestroy.as_view(),
         name='article_by_id'),

    # GET api/articles/slug
    path('/<slug:slug>', ArticleRetrieveBySlugAPIView.as_view(),
         name='article_by_slug'),
]
