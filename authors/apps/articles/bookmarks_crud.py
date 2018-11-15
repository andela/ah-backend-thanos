from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from . import models


def get_bookmarks(self):
    if not models.Article.objects.filter(pk=self.kwargs['pk']).exists():
        raise NotFound(detail="Sorry this article doesn't exist", code=404)

    bookmarks = models.Bookmark.objects.filter(article=self.kwargs['pk'])
    if not bookmarks:
        raise NotFound(detail="Sorry there are no bookmarks for this article",
                       code=404)
    return bookmarks


def create_bookmarks(self, request, article_id):
    article = get_object_or_404(models.Article, pk=article_id)
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    bookmark = models.Bookmark.objects.filter(
        article_id=article.id,
        user=request.user.id).first()
    if bookmark:
        return Response({"message": "This has already been bookmarked"}, 200)
    self.perform_create(serializer, article)
    return Response(serializer.data, 201)


def delete(self, request, article_id):
    bookmark = models.Bookmark.objects.filter(
        article_id=article_id,
        user=request.user.id).first()
    if not bookmark:
        return Response(
            {"message": "This bookmark doesn\'t exist"},
            status=status.HTTP_400_BAD_REQUEST
        )
    self.perform_destroy(bookmark)
    return Response({"message": "Bookmark succesfully deleted"}, 200)
