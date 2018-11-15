import time
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import (NotAcceptable, NotFound,
                                       ParseError,)

from .models import (Article, Comment, Thread, LikeArticle,
                     Rating, Bookmark, LikeComment,  FavoriteArticle,)
from .renderers import (ArticleRenderer, CommentRenderer,
                        ThreadRenderer, FavoriteStatusRenderer,
                        LikeStatusRenderer, RatingRenderer, BookmarkRenderer)
from .serializers import (ArticleSerializer, ArticlesUpdateSerializer,
                          CommentSerializer, ThreadCreateSerializer,
                          LikeSerializer, LikeStatusUpdateSerializer,
                          RatingSerializer, BookmarkSerializer,
                          FavoriteStatusSerializer, LikeCommentSerializer,
                          FavoriteStatusUpdateSerializer,
                          GetFavoriteArticleSerializer, TagSerializer,
                          ArticlesUpdatesSerializer)
from authors.apps.core.utils.generate_slug import generate_slug
from authors.apps.core.utils.readtime import read_time
from authors.apps.core.utils.user_management import (
    get_id_from_token,
    validate_author,
    get_id_from_token_for_viewcount
)
from authors.apps.core.utils.article_management import article_not_found
from taggit.models import Tag


class ArticlesListCreateAPIView(generics.ListCreateAPIView):
    """
    get: List all the Articles.
    post: Create an Article.
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        articles = Article.objects.all()
        if 'author' in self.request.GET:  # by author
            articles = articles.filter(
                author__username=self.request.GET['author'])
        if 'title' in self.request.GET:  # by title
            articles = articles.filter(
                title__icontains=self.request.GET['title'])
        if 'tag' in self.request.GET:  # by tag
            articles = articles.filter(
                tag_list__name__icontains=self.request.GET['tag'])
        return articles

    def create(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')
        body = request.data.get('body')
        tag_list = request.data.get('tag_list')
        image_url = request.data.get('image_url')
        audio_url = request.data.get('audio_url')

        author_id, author_username = get_id_from_token(request)

        # Add a timestamp if the slag alread exists
        slug = generate_slug(title)
        if Article.objects.filter(slug=slug).exists():
            slug += str(time.time()).replace('.', '')

        readtime = read_time(body)

        article = {
            "slug": slug,
            "title": title,
            "description": description,
            "body": body,
            "tag_list": tag_list,
            "image_url": image_url,
            "author": author_id,
            "audio_url": audio_url,
            "read_time": readtime
        }
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticleRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Retrieve a specific Article by id
    put: Update Article by id
    delete: Delete Article by id
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        article = Article.objects.get(pk=kwargs['pk'])
        if article is None:
            raise NotFound(detail="Article Not found")

        user_id = get_id_from_token_for_viewcount(request)
        if user_id != article.author.id:
            views_count = article.views_count
            views_count += 1
            fresh_article = {
                'views_count': views_count
            }
            serializer = ArticlesUpdatesSerializer(
                data=fresh_article)
            serializer.is_valid(raise_exception=True)
            serializer.update(article, fresh_article)
        return Response(
            self.serializer_class(article,
                                  context={'user_id': user_id}).data,
            status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        article_not_found(article_id)
        article = Article.objects.get(pk=kwargs['pk'])

        title = request.data.get('title', article.title)
        slug = generate_slug(title)
        if Article.objects.filter(slug=slug).exists():
            slug += str(time.time()).replace('.', '')

        author_id, author_username, = get_id_from_token(request)
        validate_author(author_id, article.author.id)

        fresh_article_data = {
            "slug": slug,
            "title": title,
            "description": request.data.get('description',
                                            article.description),
            "body": request.data.get('body', article.body),
            "tag_list": request.data.get(
                'tag_list',
                [str(tag) for tag in article.tag_list.all()]
            ),
            "image_url": request.data.get('image_url', article.image_url),
            "audio_url": request.data.get('audio_url', article.audio_url),
            "read_time": read_time(request.data.get('body'))
        }

        serializer = ArticlesUpdateSerializer(data=fresh_article_data)
        serializer.is_valid(raise_exception=True)
        serializer.update(article, fresh_article_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        article_not_found(article_id)
        article = Article.objects.get(pk=kwargs['pk'])
        author_id, username, = get_id_from_token(request)
        validate_author(author_id, article.author.id)
        self.perform_destroy(article)
        return Response({"messge": "Article deleted sucessfully"},
                        status=status.HTTP_200_OK)


class FavoriteStatusAPIView(generics.GenericAPIView):
    """
    post: Create an  favorite.
    """
    serializer_class = FavoriteStatusSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (FavoriteStatusRenderer,)
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        article_not_found(article_id)
        favorite_status = request.data.get('favorite_status')
        user, author_username = get_id_from_token(request)

        if FavoriteArticle.objects.filter(user=user)\
                          .filter(article=article_id)\
                          .exists():
            raise NotAcceptable(
                detail="You have already favorited this article",)
        article_data = Article.objects.get(pk=article_id)
        new_like_status = {
            "article": article_id,
            "article_title": article_data.title,
            "favorite_status": favorite_status,
            "user": user
        }
        serializer = self.serializer_class(data=new_like_status)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        article_not_found(article_id)
        if FavoriteArticle.objects.filter(article=article_id).exists():
            favorite_status = FavoriteArticle.objects.filter(
                article=article_id)
            favorite_statuses = FavoriteStatusSerializer(
                favorite_status, many=True)
            return Response(favorite_statuses.data, status=status.HTTP_200_OK)
        raise ParseError(detail="This article has not been favorited yet",)

    def put(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        article_not_found(article_id)
        user, author_username = get_id_from_token(request)
        current_favorite_status = FavoriteArticle.objects.filter(
            user=user).get(article=article_id)

        favorite_status_update = request.data.get(
            'favorite_status', current_favorite_status.favorite_status)
        if not FavoriteArticle.objects.filter(user=user)\
                                      .filter(article=article_id).exists():
            raise NotAcceptable(
                detail="Your not supposed to be changing this",)
        new_favorite_status = {
            "favorite_status": favorite_status_update,
        }
        serializer = FavoriteStatusUpdateSerializer(data=new_favorite_status)
        serializer.is_valid(raise_exception=True)
        serializer.update(current_favorite_status, new_favorite_status)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetFavoriteArticles(generics.ListAPIView):

    queryset = Article.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        current_user_favorites = FavoriteArticle.objects.filter(
            user=request.user, favorite_status=True)
        serializer = GetFavoriteArticleSerializer(
            current_user_favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleRetrieveBySlugAPIView(generics.RetrieveAPIView):
    """
    get: Retrieve a specific Article by slug
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'slug'


class CommentListCreateView(generics.ListCreateAPIView):
    """
    post: Create a Comment
    get: Get all Comments
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    renderer_classes = (CommentRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, article_id, *args, **kwargs):
        serializer_context = {
            'comment_author': request.user.profile,
            'article': get_object_or_404(Article, id=article_id)
        }
        serializer_data = request.data.get('comments', {})
        serializer = self.serializer_class(
            context=serializer_context,
            data=serializer_data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        if not Article.objects.filter(pk=self.kwargs['article_id']).exists():
            raise NotFound(detail="Sorry this article doesn't exist", code=404)

        comment = Comment.objects.filter(article=self.kwargs['article_id'])
        if not comment:
            raise NotFound(
                detail="Sorry there are no comments for this article",
                code=404)
        return comment


class LikeCommentAPIView(generics.GenericAPIView):
    """
    post: Create an  like or dislike.
    get: Get Like Status
    """
    serializer_class = LikeCommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (LikeStatusRenderer,)

    def post(self, request, *args, **kwargs):
        article = Article.objects.filter(pk=kwargs['article_id']).exists()
        comment = Comment.objects.filter(pk=kwargs['comment_id']).exists()

        if not article or not comment:
            raise NotFound(detail="Article or comment is Not found")
        comment_id = kwargs['comment_id']
        comment_data = Comment.objects.get(pk=kwargs['comment_id'])
        like_status = request.data.get('like_status')
        user, authour_username = get_id_from_token(request)

        new_like_status = {
            "comment": comment_data.id,
            "comment_body": comment_data.comment_body,
            "like_status": like_status,
            "user": user
        }
        serializer = self.serializer_class(data=new_like_status)
        serializer.is_valid(raise_exception=True)

        if LikeComment.objects.filter(user=user)\
                .filter(comment=comment_id)\
                .filter(like_status=like_status).exists():
            LikeComment.objects.filter(user=user)\
                .filter(comment=comment_id)\
                .filter(like_status=like_status).delete()
            message = "You have updated the your like status"
            return Response({"message": message},
                            status=status.HTTP_202_ACCEPTED)

        if LikeComment.objects.filter(user=user)\
                .filter(comment=comment_id).exists():
            LikeComment.objects.filter(user=user)\
                .filter(comment=comment_id).update(like_status=like_status)
            message = "You have updated the your like status"
            return Response(serializer.data, status=status.HTTP_200_OK)

        comment = Comment.objects.get(pk=kwargs['comment_id'])
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        article = Article.objects.filter(pk=kwargs['article_id']).exists()
        comment = Comment.objects.filter(pk=kwargs['comment_id']).exists()

        if not article or not comment:
            raise NotFound(detail="Article or comment is Not found")

        like_status = LikeComment.objects.filter(comment=kwargs['comment_id'])
        like_statuses = LikeCommentSerializer(like_status, many=True)
        return Response(like_statuses.data, status=status.HTTP_200_OK)


class LikeAPIView(generics.GenericAPIView):
    """
    post: Create an  like or dislike.
    get: Get Like Status
    """
    serializer_class = LikeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (LikeStatusRenderer,)
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        article_not_found(article_id)
        like_status = request.data.get('like_status')
        user, author_username = get_id_from_token(request)

        if LikeArticle.objects.filter(user=user)\
                              .filter(article=article_id).exists():
            raise NotAcceptable(
                detail="You have already liked/disliked this article")
        article_data = Article.objects.get(pk=article_id)
        new_like_status = {
            "article": article_id,
            "article_title": article_data.title,
            "like_status": like_status,
            "user": user
        }
        serializer = self.serializer_class(data=new_like_status)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        article_not_found(article_id)
        if LikeArticle.objects.filter(article=kwargs['pk']).exists():
            like_status = LikeArticle.objects.filter(article=kwargs['pk'])
            like_statuses = LikeSerializer(like_status, many=True)
            return Response(like_statuses.data, status=status.HTTP_200_OK)
        raise ParseError(
            detail="This article has not been liked/disliked yet",)

    def put(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        article_not_found(article_id)
        user, author_username = get_id_from_token(request)
        current_like_status = LikeArticle.objects.filter(
            user=user).get(article=article_id)

        like_status_update = request.data.get(
            'like_status', current_like_status.like_status)
        if not LikeArticle.objects.filter(user=user)\
                                  .filter(article=article_id).exists():
            raise NotAcceptable(
                detail="Your not supposed to be changing this",)

        new_like_status = {
            "like_status": like_status_update}
        serializer = LikeStatusUpdateSerializer(data=new_like_status)
        serializer.is_valid(raise_exception=True)
        serializer.update(current_like_status, new_like_status)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ThreadListCreateView(generics.ListCreateAPIView):
    """
    post: Create a thread on a comment
    get: List/Show comment thread
    """
    queryset = Thread.objects.all()
    serializer_class = ThreadCreateSerializer
    renderer_classes = (ThreadRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        serializer_context = {
            'thread_author': request.user.profile,
            'comment': get_object_or_404(Comment, id=kwargs['comment_id'])
        }
        serializer_data = request.data.get('threads', {})
        serializer = self.serializer_class(
            context=serializer_context,
            data=serializer_data,)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        if not Comment.objects.filter(pk=self.kwargs['comment_id']).exists():
            raise NotFound(
                detail="Sorry this comment doesn't exist", code=404)

        threads = Thread.objects.filter(comment=self.kwargs['comment_id'])
        if not threads:
            raise NotFound(
                detail="Sorry there are no thread comments for this article")
        return threads


class CommentDeleteView(generics.DestroyAPIView):
    """Delete a comment"""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (CommentRenderer,)
    serializer_class = CommentSerializer

    def destroy(self, request, *args, **kwargs):
        if not Comment.objects.filter(pk=kwargs['comment_id'],
                                      article=kwargs['article_id']).exists():
            raise NotFound(detail=" Comment Not found")

        comment = Comment.objects.get(pk=kwargs['comment_id'])
        author_id, username = get_id_from_token(request)
        validate_author(author_id, comment.comment_author.id)
        self.perform_destroy(comment)
        return Response({"message": "Comment deleted sucessfully"},
                        status=status.HTTP_200_OK)


class ArticleRating(generics.ListCreateAPIView):
    """
    post: rate an article
    """
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    renderer_classes = (RatingRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        if not Article.objects.filter(pk=article_id).exists():
            raise NotFound(detail="Article Not found")
        rating = request.data.get('rating')
        message = "Score value must be between `0` and `5`"
        if rating > 5 or rating < 0:
            raise ParseError(detail=message)
        reader, author_username, = get_id_from_token(request)

        article = Article.objects.get(pk=article_id)
        article_author = article.author.id

        if int(article_author) == int(reader):
            raise ParseError(detail="You can't rate your article")

        if Rating.objects.filter(
                reader=reader).filter(article=article.id).exists():
            raise ParseError(detail="You already rated this article")

        rating = {
            "article": article.id,
            "rating": rating,
            "reader": reader
        }
        serializer = self.serializer_class(data=rating)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookmarkListCreateView(generics.ListCreateAPIView):
    """
    get: List Bookmarks
    post: Bookmark an Article
    """
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    renderer_classes = (BookmarkRenderer,)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['pk'])
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        bookmark = Bookmark.objects.filter(article_id=article.id,
                                           user=request.user.id).first()
        if bookmark:
            return Response({"message": "This has already been bookmarked"})
        self.perform_create(serializer, article)
        return Response(serializer.data, 201)

    def perform_create(self, serializer, article):
        serializer.save(user=self.request.user, article=article)


class BookmarkDestroyView(generics.DestroyAPIView):
    """
    delete: Delete a Bookmark
    """
    queryset = Article.objects.all()
    serializer_class = BookmarkSerializer
    renderer_classes = (BookmarkRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'article_id'

    def destroy(self, request, *args, **kwargs):
        bookmark = Bookmark.objects.filter(article_id=kwargs['article_id'],
                                           user=request.user.id).first()
        if not bookmark:
            return Response({"message": "This bookmark doesn\'t exist"},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(bookmark)
        return Response({"message": "Bookmark succesfully deleted"}, 200)


class TagsListAPIView(generics.ListAPIView):
    """
    get: List all Tags (categories).
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
