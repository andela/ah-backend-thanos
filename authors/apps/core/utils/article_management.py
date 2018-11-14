from rest_framework.exceptions import NotFound
from rest_framework import serializers
from authors.apps.articles.models import Article
from authors.apps.core.utils.user_management import get_id_from_token


def article_not_found(article_id):
    if not Article.objects.filter(pk=article_id).exists():
        raise NotFound(detail="Article Not found",)


def validate_article_get_user(request, article_id):
    article_not_found(article_id)
    user, author_username = get_id_from_token(request)
    return user


def add_views_to_article(current_user_id, article):
    if current_user_id != article.author.id:
        views_count = article.views_count
        views_count += 1
        fresh_article = {
            'views_count': views_count
        }
        serializer = serializers.ArticlesUpdatesSerializer(
            data=fresh_article)
        serializer.is_valid(raise_exception=True)
        serializer.update(article, fresh_article)


def get_article_from_db(article_id):
    article_not_found(article_id)
    return Article.objects.get(pk=article_id)
