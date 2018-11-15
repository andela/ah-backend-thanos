from rest_framework import status, generics, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (Article, Comment, Thread, Rating, Bookmark)
from . import (
    renderers, serializers, articles_crud, favorites_crud, filters,
    comments_crud, likes_crud, threads_crud, ratings_crud, bookmarks_crud,
    report_crud)
from authors.apps.core.utils.user_management import (
    get_id_from_token, get_id_from_token_for_viewcount)
from authors.apps.core.utils.article_management import (
    add_views_to_article, get_article_from_db)
from taggit.models import Tag


class ArticlesListCreateAPIView(generics.ListCreateAPIView):
    """
    get: List all or Search Articles.
    post: Create an Article.
    """
    queryset = Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    renderer_classes = (renderers.ArticleRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = filters.ArticlesFilter

    def create(self, request, *args, **kwargs):
        author_id, author_username = get_id_from_token(request)
        return articles_crud.create_article(request, author_id)


class ArticleRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Retrieve a specific Article by id
    put: Update Article by id
    delete: Delete Article by id
    """
    queryset = Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    renderer_classes = (renderers.ArticleRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        article = get_article_from_db(kwargs['pk'])
        user_id = get_id_from_token_for_viewcount(request)
        add_views_to_article(user_id, article)
        return Response(
            self.serializer_class(article,
                                  context={'user_id': user_id}).data,
            status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return articles_crud.update_article(request, kwargs['pk'])

    def destroy(self, request, *args, **kwargs):
        return articles_crud.delete_article(self, request, kwargs['pk'])


class FavoriteStatusAPIView(generics.GenericAPIView):
    """
    post: Favorite an article.
    get: Get favourate status of an article
    put: Update favourate status
    """
    serializer_class = serializers.FavoriteStatusSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (renderers.FavoriteStatusRenderer,)
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):
        return favorites_crud.favorite_an_article(self, request, kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return favorites_crud.get_favorite_status(kwargs['pk'])

    def put(self, request, *args, **kwargs):
        return favorites_crud.udpate_favorite(request, kwargs['pk'])


class GetFavoriteArticles(generics.ListAPIView):
    """get: Retrieve all user's favourate articles"""
    queryset = Article.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        return favorites_crud.list_favorites(request)


class ArticleRetrieveBySlugAPIView(generics.RetrieveAPIView):
    """get: Retrieve a specific Article by slug"""
    queryset = Article.objects.all()
    serializer_class = serializers.ArticleSerializer
    renderer_classes = (renderers.ArticleRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'slug'


class CommentListCreateView(generics.ListCreateAPIView):
    """
    post: Create a Comment
    get: Get all Comments
    """
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    renderer_classes = (renderers.CommentRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, article_id, *args, **kwargs):
        return comments_crud.create_comment(self, request, article_id)

    def get_queryset(self):
        return comments_crud.get_comments(self, self.kwargs['article_id'])


class CommentDeleteView(generics.DestroyAPIView):
    """Delete a comment"""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (renderers.CommentRenderer,)
    serializer_class = serializers.CommentSerializer

    def destroy(self, request, *args, **kwargs):
        return comments_crud.delete_comment(
            self, request, kwargs['comment_id'], kwargs['article_id'])


class LikeCommentAPIView(generics.GenericAPIView):
    """
    post: Create an  like or dislike.
    get: Get Like Status
    put: Update Like Status
    """
    serializer_class = serializers.LikeCommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (renderers.LikeStatusRenderer,)

    def post(self, request, *args, **kwargs):
        return likes_crud.like_comment(self, request, kwargs['article_id'],
                                       kwargs['comment_id'])

    def get(self, request, *args, **kwargs):
        return likes_crud.get_comment_likes(kwargs['article_id'],
                                            kwargs['comment_id'])


class LikeAPIView(generics.GenericAPIView):
    """
    post: Create a like or dislike.
    get: Get Like Status.
    put: Update a Like or a Dislike
    """
    serializer_class = serializers.LikeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (renderers.LikeStatusRenderer,)
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):
        return likes_crud.like_article(self, request, kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return likes_crud.get_like_status(kwargs['pk'])

    def put(self, request, *args, **kwargs):
        return likes_crud.edit_like_status(request, kwargs['pk'])


class ThreadListCreateView(generics.ListCreateAPIView):
    """
    post: Create a thread on a comment
    get: List/Show comment thread
    """
    queryset = Thread.objects.all()
    serializer_class = serializers.ThreadCreateSerializer
    renderer_classes = (renderers.ThreadRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        return threads_crud.create_comment_thread(self, request,
                                                  kwargs['comment_id'])

    def get_queryset(self):
        return threads_crud.get_comment_thread(self.kwargs['comment_id'])


class ArticleRating(generics.CreateAPIView):
    """
    get: list ratings
    post: rate an article
    """
    queryset = Rating.objects.all()
    serializer_class = serializers.RatingSerializer
    renderer_classes = (renderers.RatingRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        return ratings_crud.create_rating(self, request, kwargs['pk'])


class BookmarkListCreateView(generics.ListCreateAPIView):
    """
    get: List Bookmarks
    post: Bookmark an Article
    """
    queryset = Bookmark.objects.all()
    serializer_class = serializers.BookmarkSerializer
    renderer_classes = (renderers.BookmarkRenderer,)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        return bookmarks_crud.create_bookmarks(self, request, kwargs['pk'])

    def perform_create(self, serializer, article):
        serializer.save(user=self.request.user, article=article)

    def get_queryset(self):
        return bookmarks_crud.get_bookmarks(self)


class BookmarkDestroyView(generics.DestroyAPIView):
    """delete: Delete a Bookmark"""
    serializer_class = serializers.BookmarkSerializer
    renderer_classes = (renderers.BookmarkRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'article_id'

    def destroy(self, request, *args, **kwargs):
        return bookmarks_crud.delete(self, request, kwargs['article_id'])


class TagsListAPIView(generics.ListAPIView):
    """get: List all Tags (categories)."""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (permissions.AllowAny,)


class ReportArticleAPIView(generics.CreateAPIView):
    """Post: Report an article"""
    serializer_class = serializers.ReportArticleSerializer
    renderer_classes = (renderers.ReportArticleRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'article_id'

    def create(self, request, article_id, *args, **kwargs):
        return report_crud.report_article(self, request, article_id)
