from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from . import models
from authors.apps.core.utils.article_management import article_not_found
from authors.apps.core.utils.user_management import get_id_from_token


def create_rating(self, request, article_id):
    article_not_found(article_id)
    rating = request.data.get('rating')
    message = "Score value must be between `0` and `5`"
    if rating > 5 or rating < 0:
        raise ParseError(detail=message)
    reader, author_username, = get_id_from_token(request)

    article = models.Article.objects.get(pk=article_id)
    article_author = article.author.id

    if int(article_author) == int(reader):
        raise ParseError(detail="You can't rate your article")

    if models.Rating.objects.filter(
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
