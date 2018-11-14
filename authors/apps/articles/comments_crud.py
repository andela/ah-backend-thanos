from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from . import models
from authors.apps.core.utils.user_management import (
    get_id_from_token, validate_author)


def get_comments(self, article_pk):
    if not models.Article.objects.filter(pk=article_pk).exists():
        raise NotFound(detail="Sorry this article doesn't exist", code=404)

    comments = models.Comment.objects.filter(article=self.kwargs['article_id'])
    if not comments:
        raise NotFound(
            detail="Sorry there are no comments for this article",
            code=404)
    return comments


def create_comment(self, request, article_pk):
    serializer_context = {
        'comment_author': request.user.profile,
        'article': get_object_or_404(models.Article, id=article_pk)
    }
    serializer_data = request.data.get('comments', {})
    serializer = self.serializer_class(
        context=serializer_context,
        data=serializer_data,
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_comment(self, request, comment_id, article_id):
    if not models.Comment.objects.filter(pk=comment_id,
                                         article=article_id).exists():
        raise NotFound(detail=" Comment Not found")

    comment = models.Comment.objects.get(pk=comment_id)
    author_id, username = get_id_from_token(request)
    validate_author(author_id, comment.comment_author.id)
    self.perform_destroy(comment)
    return Response({"message": "Comment deleted sucessfully"},
                    status=status.HTTP_200_OK)
