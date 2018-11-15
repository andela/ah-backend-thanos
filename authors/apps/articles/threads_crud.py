from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from . import models


def create_comment_thread(self, request, comment_id):
    serializer_context = {
        'thread_author': request.user.profile,
        'comment': get_object_or_404(models.Comment, id=comment_id)
    }
    serializer_data = request.data.get('threads', {})
    serializer = self.serializer_class(
        context=serializer_context,
        data=serializer_data,)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def get_comment_thread(comment_id):
    if not models.Comment.objects.filter(pk=comment_id).exists():
        raise NotFound(detail="Sorry this comment doesn't exist", code=404)

    threads = models.Thread.objects.filter(comment=comment_id)
    if not threads:
        raise NotFound(
            detail="Sorry there are no thread comments for this article")
    return threads
