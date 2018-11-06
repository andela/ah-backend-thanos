import re
import time
import jwt
from django.conf import settings

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from .models import Article
from .renderers import ArticleRenderer
from .serializers import ArticleSerializer
from authors.apps.authentication.models import User


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
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, 'utf-8')
            author = payload['id']
        except Exception as exception:
            raise APIException({
                "error": "Login Token required. System Error Response: " +
                str(exception)
                })

        # slug: Allow only alphanumeric values and dashes for spaces
        slug = ''
        for i in re.split(r'(.)', title.strip().lower()):
            if i.isalnum():
                slug += i
            elif i == ' ':
                slug += '-'

        # Add a timestamp if the slag alread exists
        if Article.objects.filter(slug=slug).exists():
            slug += str(time.time()).replace('.', '')

        article = {
            "slug": slug,
            "title": title,
            "description": description,
            "body": body,
            "tag_list": tag_list,
            "image_url": image_url,
            "author": author,
            "audio_url": audio_url
        }
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticleRetrieveByIdAPIView(generics.RetrieveAPIView):
    """
    get: Retrieve a specific Article by id
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleRenderer,)
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'pk'


class ArticleRetrieveBySlugAPIView(generics.RetrieveAPIView):
    """
    get: Retrieve a specific Article by slug
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleRenderer,)
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'
