import jwt

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed

from rest_framework.exceptions import NotFound, ParseError

from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile


def get_id_from_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    payload = jwt.decode(token, settings.SECRET_KEY, 'utf-8')
    return payload['id'], payload['username']


def get_id_from_token_for_viewcount(request):
    if request.user == AnonymousUser():
        return 0
    else:
        auth = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')
        token = auth[1]
        payload = jwt.decode(token, settings.SECRET_KEY, 'utf-8')
        return payload['id']


def validate_author(current_user_id, author_id):
    """Retrict user from editing or deleting if not authorized"""
    if current_user_id != author_id:
        raise AuthenticationFailed(
            detail="You do not have permissions to this Article",
            )


def getUserFromDatabase(pk=0, username=""):
    """Get user from the database by id or username"""
    if User.objects.filter(pk=pk).exists():
        return User.objects.get(pk=pk)
    elif User.objects.filter(username=username).exists():
        return User.objects.get(username=username)
    else:
        raise NotFound(detail="User Not found")


def getProfileFromDatabase(user_id):
    if Profile.objects.filter(user=user_id).exists():
        return Profile.objects.get(user=user_id)
    else:
        raise NotFound(detail="Profile Not found")


def validateCurrentUserSelectedUser(current_user_id, selected_user_id):
    if current_user_id == selected_user_id:
        raise ParseError(
            detail="The current user is the same as the selected user"
        )
