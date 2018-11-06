from rest_framework.exceptions import AuthenticationFailed


class UserCannotEditProfile(AuthenticationFailed):
    status_code = 403
    default_detail = "Sorry, you cannot edit another users profile"
