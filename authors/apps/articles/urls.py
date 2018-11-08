from django.urls import path

from .views import (
    ArticlesListCreateAPIView,
    ArticleRetrieveUpdateDestroy,
    ArticleRetrieveBySlugAPIView,
    CommentListCreateView,
    ThreadListCreateView,
    CommentRetrieveDeleteView
)

urlpatterns = [
    # GET/POST api/articles
    path('', ArticlesListCreateAPIView.as_view(), name='list_create'),
    # GET api/articles/id
    path('<int:pk>', ArticleRetrieveUpdateDestroy.as_view(),
         name='article_by_id'),
    # GET api/articles/slug
    path('<slug:slug>', ArticleRetrieveBySlugAPIView.as_view(),
         name='article_by_slug'),
    path('<int:pk>/comments', CommentListCreateView.as_view(),
         name='comment_on_article'),
    path('<int:pk>/comments/<int:id>',
         CommentRetrieveDeleteView.as_view(),
         name='comment_by_id'),
    path('<int:pk>/comments/<int:id>/threads',
         ThreadListCreateView.as_view(),
         name='comment_on_comment'),

]
