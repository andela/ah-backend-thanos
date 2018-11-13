from rest_framework.exceptions import NotFound
from authors.apps.articles.models import Article


def article_not_found(article_id):
    if not Article.objects.filter(pk=article_id).exists():
            raise NotFound(detail="Article Not found",)
