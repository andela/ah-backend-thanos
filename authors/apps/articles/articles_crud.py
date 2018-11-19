from rest_framework.response import Response
from rest_framework import status
from . import serializers, models
from authors.apps.core.utils.generate_slug import generate_slug
from authors.apps.core.utils.article_management import (
    get_article_from_db, article_not_found)
from authors.apps.core.utils.user_management import (
    get_id_from_token, validate_author)
from authors.apps.core.utils.readtime import read_time
from authors.apps.core.tasks import notification
from ...settings import TESTING


def create_article(request, author_id):
    title = request.data.get('title')
    body = request.data.get('body')
    slug = generate_slug(title)
    readtime = read_time(body)
    article_data = {
        "slug": slug,
        "title": title,
        "author": author_id,
        "body": body,
        "read_time": readtime,
        "tag_list": request.data.get('tag_list'),
        "image_url": request.data.get('image_url'),
        "audio_url": request.data.get('audio_url'),
        "description": request.data.get('description'),
    }
    serializer = serializers.ArticleSerializer(data=article_data)
    serializer.is_valid(raise_exception=True)
    if TESTING is True:
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif TESTING is False:  # pragma: no cover
        notification.delay(author_id)  # pragma: no cover
        serializer.save()  # pragma: no cover
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # pragma: no cover


def update_article(request, article_pk):
    article = get_article_from_db(article_pk)
    title = request.data.get('title', article.title)
    slug = generate_slug(title)
    author_id, author_username, = get_id_from_token(request)
    validate_author(author_id, article.author.id)
    fresh_data = {
        "slug": slug,
        "title": title,
        "body": request.data.get('body', article.body),
        "image_url": request.data.get('image_url', article.image_url),
        "audio_url": request.data.get('audio_url', article.audio_url),
        "read_time": read_time(request.data.get('body')),
        "description": request.data.get(
            'description',
            article.description),
        "tag_list": request.data.get(
            'tag_list',
            [str(tag) for tag in article.tag_list.all()]
        ),
    }
    serializer = serializers.ArticlesUpdateSerializer(data=fresh_data)
    serializer.is_valid(raise_exception=True)
    serializer.update(article, fresh_data)
    return Response(serializer.data, status=status.HTTP_200_OK)


def delete_article(self, request, article_id):
    article_not_found(article_id)
    article = models.Article.objects.get(pk=article_id)
    author_id, username, = get_id_from_token(request)
    validate_author(author_id, article.author.id)
    self.perform_destroy(article)
    return Response(
        {"message": "Article deleted sucessfully"},
        status=status.HTTP_200_OK
    )
