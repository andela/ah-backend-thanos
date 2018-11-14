from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAcceptable, ParseError, NotFound
from . import models, serializers
from authors.apps.core.utils.article_management import (
    validate_article_get_user, get_id_from_token)
from authors.apps.core.utils.article_management import (
    article_not_found)


def like_article(self, request, article_pk):
    user = validate_article_get_user(request, article_pk)
    like_status = request.data.get('like_status')

    if models.LikeArticle.objects.filter(user=user)\
                                 .filter(article=article_pk).exists():
        raise NotAcceptable(
            detail="You have already liked/disliked this article")
    article_data = models.Article.objects.get(pk=article_pk)
    new_like_status = {
        "article": article_pk,
        "article_title": article_data.title,
        "like_status": like_status,
        "user": user
    }
    serializer = self.serializer_class(data=new_like_status)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def get_like_status(article_pk):
    article_not_found(article_pk)
    if models.LikeArticle.objects.filter(article=article_pk).exists():
        like_status = models.LikeArticle.objects.filter(article=article_pk)
        like_statuses = serializers.LikeSerializer(like_status, many=True)
        return Response(like_statuses.data, status=status.HTTP_200_OK)
    raise ParseError(detail="This article has not been liked/disliked yet",)


def edit_like_status(request, article_pk):
    user = validate_article_get_user(request, article_pk)
    current_like_status = models.LikeArticle.objects.filter(
        user=user).get(article=article_pk)

    like_status_update = request.data.get(
        'like_status',
        current_like_status.like_status
    )
    if not models.LikeArticle.objects.filter(user=user)\
                                     .filter(article=article_pk).exists():
        raise NotAcceptable(detail="Your not supposed to be changing this",)
    new_like_status = {"like_status": like_status_update}
    serializer = serializers.LikeStatusUpdateSerializer(data=new_like_status)
    serializer.is_valid(raise_exception=True)
    serializer.update(current_like_status, new_like_status)
    return Response(serializer.data, status=status.HTTP_200_OK)


def like_comment(self, request, article_pk, comment_pk):
    article = models.Article.objects.filter(pk=article_pk).exists()
    comment = models.Comment.objects.filter(pk=comment_pk).exists()

    if not article or not comment:
        raise NotFound(detail="Article or comment is Not found")
    comment_data = models.Comment.objects.get(pk=comment_pk)
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

    if models.LikeComment.objects.filter(user=user)\
            .filter(comment=comment_pk)\
            .filter(like_status=like_status).exists():
        models.LikeComment.objects.filter(user=user)\
            .filter(comment=comment_pk)\
            .filter(like_status=like_status).delete()
        message = "You have updated the your like status"
        return Response({"message": message}, status=status.HTTP_202_ACCEPTED)

    if models.LikeComment.objects.filter(user=user)\
            .filter(comment=comment_pk).exists():
        models.LikeComment.objects.filter(user=user)\
            .filter(comment=comment_pk).update(like_status=like_status)
        message = "You have updated the your like status"
        return Response(serializer.data, status=status.HTTP_200_OK)

    comment = models.Comment.objects.get(pk=comment_pk)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def get_comment_likes(article_id, comment_id):
    article = models.Article.objects.filter(pk=article_id).exists()
    comment = models.Comment.objects.filter(pk=comment_id).exists()

    if not article or not comment:
        raise NotFound(detail="Article or comment is Not found")

    like_status = models.LikeComment.objects.filter(comment=comment_id)
    like_statuses = serializers.LikeCommentSerializer(like_status, many=True)
    return Response(like_statuses.data, status=status.HTTP_200_OK)
