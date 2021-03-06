from django.urls import path
from authors.apps.articles.share_articles import (
    ShareEmailAPIView, ShareFacebookAPIView, ShareTwitterAPIView)

from .views import (
    ArticlesListCreateAPIView, ArticleRetrieveUpdateDestroy,
    ArticleRetrieveBySlugAPIView, CommentListCreateView,
    ThreadListCreateView, CommentDeleteView, LikeAPIView,
    ArticleRating, FavoriteStatusAPIView, GetFavoriteArticles,
    BookmarkListCreateView, BookmarkDestroyView, TagsListAPIView,
    ReportArticleAPIView, LikeCommentAPIView,
)


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
    path('articles/<int:pk>/rating', ArticleRating.as_view(),
         name='ratings_list'),
    path('articles/<int:pk>/bookmarks', BookmarkListCreateView.as_view(),
         name='create_bookmark'),
    path('articles/<int:article_id>/bookmark', BookmarkDestroyView.as_view(),
         name='un_bookmark'),
    path('articles/<int:pk>/favorite_status', FavoriteStatusAPIView.as_view(),
         name='favorite_article'),
    path('articles/favorites/',
         GetFavoriteArticles.as_view(),
         name='favorites'),
    path('tags', TagsListAPIView.as_view()),
    path('articles/<int:article_id>/comments/<int:comment_id>/like_status',
         LikeCommentAPIView.as_view(), name='like_comment'),
    path('articles/<int:article_id>/email',
         ShareEmailAPIView.as_view(), name='share_email'),
    path('articles/<int:article_id>/facebook',
         ShareFacebookAPIView.as_view(), name='share_facebook'),
    path('articles/<int:article_id>/twitter',
         ShareTwitterAPIView.as_view(), name='share_twitter'),


    path('articles/<int:article_id>/report', ReportArticleAPIView.as_view(),
         name='report_article')
]
