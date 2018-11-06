from django.urls import path

from .views import (
    ArticlesListCreateAPIView, ArticleRetrieveUpdateDestroy,
    ArticleRetrieveBySlugAPIView, CommentListCreateView,
    ThreadListCreateView, CommentRetrieveDeleteView, LikeAPIView,
    UpdateLikeStatusAPIView)

urlpatterns = [
    # GET/POST api/articles
    path('', ArticlesListCreateAPIView.as_view(), name='list_create'),
    # GET api/articles/id
    path('articles/<int:pk>', ArticleRetrieveUpdateDestroy.as_view(),
         name='article_by_id'),
    # GET api/articles/slug
    path('articles/<slug:slug>', ArticleRetrieveBySlugAPIView.as_view(),
         name='article_by_slug'),
    path('articles/<int:pk>/comments', CommentListCreateView.as_view(),
         name='comment_on_article'),
    path('articles/<int:pk>/comments/<int:id>',
         CommentRetrieveDeleteView.as_view(),
         name='comment_by_id'),
    path('articles/<int:pk>/comments/<int:id>/threads',
         ThreadListCreateView.as_view(),
         name='comment_on_comment'),
    path('articles/<int:pk>/like_status', LikeAPIView.as_view(),
         name='like_article'),
    path('articles/<int:pk>/like_status_update',
         UpdateLikeStatusAPIView.as_view(),
         name='like_article_update'),

]
