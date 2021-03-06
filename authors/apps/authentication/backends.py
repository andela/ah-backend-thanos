import jwt

from django.conf import settings

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from authors.apps.authentication.models import User


class JWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        """
        This method is called for on every request and it
        returns a two-tuple of (user, token) if authentication is
        successfull and a None otherwise.
        If any fails we raise `AuthenticationFailed` and Django rest framework
        does the rest.
        """
        request.user = None

        authentication_header = authentication.get_authorization_header(
            request).split()

        if not authentication_header:
            # NO authentication header value was entered
            return None

        token = authentication_header[1].decode('utf-8')
        # if all the above is passed, we then go one to authenticate
        # the given credentials.
        return self.authenticate_user_details(token)

    def authenticate_user_details(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except Exception:
            raise AuthenticationFailed(detail="Invalid/expired token",
                                       code=403)

        user = User.objects.get(pk=payload['id'])
        # No endpoint that deactivates a user for now
        # if not user.is_active:
        #     raise exceptions.AuthenticationFailed(
        #         'User is currently either inactive or deleted')

        return (user, token)
