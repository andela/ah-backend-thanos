import time
import re

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response

from .models import Article, Comment, Thread, LikeArticle, Rating
from .renderers import (ArticleRenderer, CommentRenderer, ThreadRenderer,
                        LikeStatusRenderer, RatingRenderer)
from .serializers import (ArticleSerializer, ArticlesUpdateSerializer,
                          CommentSerializer, ThreadCreateSerializer,
                          LikeSerializer, LikeStatusUpdateSerializer,
                          RatingSerializer)
from rest_framework.exceptions import (NotAcceptable, NotFound,
                                       ParseError,)
from rest_framework.exceptions import NotFound


from authors.apps.core.utils.generate_slug import generate_slug
from authors.apps.core.utils.user_management import (
    get_id_from_token,
    validate_author
)
from rest_framework.exceptions import (ParseError,)


class ArticlesListCreateAPIView(generics.ListCreateAPIView):
    """
    get: List all the Articles.
    post: Create an Article.
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')
        body = request.data.get('body')
        tag_list = request.data.get('tag_list')
        image_url = request.data.get('image_url')
        audio_url = request.data.get('audio_url')

        # slug: Allow only alphanumeric values and dashes for spaces
        slug = ''
        for i in re.split(r'(.)', title.strip().lower()):
            if i.isalnum():
                slug += i
            elif i == ' ':
                slug += '-'

        author_id, author_username = get_id_from_token(request)

        # Add a timestamp if the slag alread exists
        slug = generate_slug(title)
        if Article.objects.filter(slug=slug).exists():
            slug += str(time.time()).replace('.', '')

        article = {
            "slug": slug,
            "title": title,
            "description": description,
            "body": body,
            "tag_list": tag_list,
            "image_url": image_url,
            "author": author_id,
            "audio_url": audio_url
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

    def update(self, request, *args, **kwargs):
        if not Article.objects.filter(pk=kwargs['pk']).exists():
            raise NotFound(detail="Article Not found",)
        article = Article.objects.get(pk=kwargs['pk'])
        print(article)
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
            "tag_list": request.data.get('tag_list', article.tag_list),
            "image_url": request.data.get('image_url', article.image_url),
            "audio_url": request.data.get('audio_url', article.audio_url)
        }

        serializer = ArticlesUpdateSerializer(data=fresh_article_data)
        serializer.is_valid(raise_exception=True)
        serializer.update(article, fresh_article_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not Article.objects.filter(pk=kwargs['pk']).exists():
            raise NotFound(detail="Article Not found",)
        article = Article.objects.get(pk=kwargs['pk'])
        author_id, username, = get_id_from_token(request)
        validate_author(author_id, article.author.id)
        self.perform_destroy(article)
        return Response({"messge": "Article deleted sucessfully"},
                        status=status.HTTP_200_OK)


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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    renderer_classes = (CommentRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, pk, *args, **kwargs):
        serializer_context = {
            'author': request.user.profile,
            'article': get_object_or_404(Article, id=pk)
        }
        serializer_data = request.data.get('comments', {})
        serializer = self.serializer_class(
            context=serializer_context,
            data=serializer_data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        if not Article.objects.filter(pk=kwargs['pk']).exists():
            raise NotFound(detail="Sorry this article doesn't exist", code=404)

        comment = Comment.objects.filter(article=kwargs['pk'])
        if not comment:
            raise NotFound(
                detail="Sorry there are no comments for this article",
                code=404)
        serializer = self.serializer_class(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeAPIView(generics.GenericAPIView):
    """
    post: Create an  like or dislike.
    """
    serializer_class = LikeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (LikeStatusRenderer,)
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):
        if not Article.objects.filter(pk=kwargs['pk']).exists():
            raise NotFound(detail="Article Not found")
        article_id = kwargs['pk']
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
        if not Article.objects.filter(pk=kwargs['pk']).exists():
            raise NotFound(detail="Article Not found")
        if LikeArticle.objects.filter(article=kwargs['pk']).exists():
            like_status = LikeArticle.objects.filter(article=kwargs['pk'])
            like_statuses = LikeSerializer(like_status, many=True)
            return Response(like_statuses.data, status=status.HTTP_200_OK)
        raise ParseError(
            detail="This article has not been liked/disliked yet",)


class ThreadListCreateView(generics.ListCreateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadCreateSerializer
    renderer_classes = (ThreadRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        serializer_context = {
            'author': request.user.profile,
            'comment': get_object_or_404(Comment, id=kwargs['id'])
        }
        serializer_data = request.data.get('threads', {})
        serializer = self.serializer_class(
            context=serializer_context,
            data=serializer_data,)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        if not Comment.objects.filter(pk=kwargs['id']).exists():
            raise NotFound(
                detail="Sorry this comment doesn't exist", code=404)

        threads = Thread.objects.filter(comment=kwargs['id'])
        if not threads:
            raise NotFound(
                detail="Sorry there are no thread comments for this article")
        serializer = self.serializer_class(threads, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    """Retrive and Delete a comment"""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (CommentRenderer,)
    serializer_class = CommentSerializer

    def get(self, request, *args, **kwargs):

        comment = get_object_or_404(Comment, id=kwargs['id'])

        serializer = self.serializer_class(comment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not Comment.objects.filter(pk=kwargs['id']).exists():
            raise NotFound(detail="Not found")

        comment = Comment.objects.get(pk=kwargs['id'])
        author_id, username = get_id_from_token(request)
        validate_author(author_id, comment.author.id)
        self.perform_destroy(comment)
        return Response({"message": "Comment deleted sucessfully"},
                        status=status.HTTP_200_OK)


class UpdateLikeStatusAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = LikeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = (LikeStatusRenderer,)
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        article_id = kwargs['pk']
        if not Article.objects.filter(pk=article_id).exists():
            raise NotFound(detail="Article Not found")
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
            "like_status": like_status_update,
        }
        serializer = LikeStatusUpdateSerializer(data=new_like_status)
        serializer.is_valid(raise_exception=True)
        serializer.update(current_like_status, new_like_status)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        rating = request.data.get('rating')
        if rating > 5 or rating < 0:
            raise ParseError(
                detail="Score value must not go below `0` and not go beyond `5`")

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
