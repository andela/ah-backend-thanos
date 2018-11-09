from django.urls import path

from .views import (
    ArticlesListCreateAPIView, ArticleRetrieveUpdateDestroy,
    ArticleRetrieveBySlugAPIView, CommentListCreateView,
    ThreadListCreateView, CommentDeleteView, LikeAPIView,
    UpdateLikeStatusAPIView, BookmarkListCreateView,
    BookmarkDestroyView, ArticleRating,)

urlpatterns = [

    # GET/POST api/articles
    path('articles', ArticlesListCreateAPIView.as_view(), name='list_create'),
    # GET api/articles/id
    path('articles/<int:pk>', ArticleRetrieveUpdateDestroy.as_view(),
         name='article_by_id'),
    # GET api/articles/slug
    path('articles/<slug:slug>', ArticleRetrieveBySlugAPIView.as_view(),
         name='article_by_slug'),
    path('articles/<int:article_id>/comments', CommentListCreateView.as_view(),
         name='comment_on_article'),
    path('articles/<int:article_id>/comments/<int:comment_id>',
         CommentDeleteView.as_view(),
         name='comment_by_id'),
    path('articles/<int:article_id>/comments/<int:comment_id>/threads',
         ThreadListCreateView.as_view(),
         name='comment_on_comment'),
    path('articles/<int:pk>/like_status', LikeAPIView.as_view(),
         name='like_article'),
    path('articles/<int:pk>/like_status_update',
         UpdateLikeStatusAPIView.as_view(),
         name='like_article_update'),

    # GET/POST api/ratings
    path('articles/<int:pk>/rating', ArticleRating.as_view(),
         name='ratings_list'),
    path('articles/<int:pk>/bookmarks', BookmarkListCreateView.as_view(),
         name='create_bookmark'),

    path('articles/<int:article_id>/bookmark', BookmarkDestroyView.as_view(),
         name='un_bookmark'),
]
