import jwt

from django.conf import settings
from rest_framework.exceptions import APIException


def get_id_from_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    payload = jwt.decode(token, settings.SECRET_KEY, 'utf-8')
    return payload['id'], payload['username']


def validate_author(current_user_id, author_id):
    if current_user_id != author_id:
        raise APIException(
            {"error": "You do not have permission to edit this Article"})
