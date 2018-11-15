from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAcceptable, ParseError
from authors.apps.core.utils.article_management import (
    validate_article_get_user)
from authors.apps.core.utils.article_management import (
    article_not_found)
from . import models, serializers


def list_favorites(request):
    current_user_favorites = models.FavoriteArticle.objects.filter(
        user=request.user, favorite_status=True)
    serializer = serializers.GetFavoriteArticleSerializer(
        current_user_favorites, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def favorite_an_article(self, request, article_pk):
    user = validate_article_get_user(request, article_pk)
    favorite_status = request.data.get('favorite_status')

    if models.FavoriteArticle.objects.filter(user=user)\
                             .filter(article=article_pk)\
                             .exists():
        raise NotAcceptable(detail="You have already favorited this article",)
    article_data = models.Article.objects.get(pk=article_pk)
    new_like_status = {
        "article": article_pk,
        "article_title": article_data.title,
        "favorite_status": favorite_status,
        "user": user
    }
    serializer = self.serializer_class(data=new_like_status)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def get_favorite_status(article_id):
    article_not_found(article_id)
    if models.FavoriteArticle.objects.filter(article=article_id).exists():
        favorite_status = models.FavoriteArticle.objects.filter(
            article=article_id)
        favorite_statuses = serializers.FavoriteStatusSerializer(
            favorite_status, many=True)
        return Response(favorite_statuses.data, status=status.HTTP_200_OK)
    raise ParseError(detail="This article has not been favorited yet",)


def udpate_favorite(request, article_pk):
    user = validate_article_get_user(request, article_pk)
    current_favorite_status = models.FavoriteArticle.objects.filter(
        user=user).get(article=article_pk)

    favorite_status_update = request.data.get(
        'favorite_status', current_favorite_status.favorite_status)
    if not models.FavoriteArticle.objects.filter(user=user)\
                                         .filter(article=article_pk).exists():
        raise NotAcceptable(detail="Your not supposed to be changing this",)
    new_favorite_status = {"favorite_status": favorite_status_update, }
    serializer = serializers.FavoriteStatusUpdateSerializer(
        data=new_favorite_status)
    serializer.is_valid(raise_exception=True)
    serializer.update(current_favorite_status, new_favorite_status)
    return Response(serializer.data, status=status.HTTP_200_OK)
