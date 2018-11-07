import time

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .models import Article
from .renderers import ArticleRenderer
from .serializers import ArticleSerializer, ArticlesUpdateSerializer

from authors.apps.core.utils.generate_slug import generate_slug
from authors.apps.core.utils.user_management import (
    get_id_from_token,
    validate_author
)


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
            raise NotFound(detail="Article Not found", code=404)
        article = Article.objects.get(pk=kwargs['pk'])

        title = request.data.get('title', article.title)
        slug = generate_slug(title)
        if Article.objects.filter(slug=slug).exists():
            slug += str(time.time()).replace('.', '')

        author_id, author_username = get_id_from_token(request)
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
            raise NotFound(detail="Article Not found", code=404)
        article = Article.objects.get(pk=kwargs['pk'])
        author_id, username = get_id_from_token(request)
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
