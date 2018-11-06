from rest_framework.exceptions import APIException


class UserCannotEditProfile(APIException):
    status_code = 403
    default_detail = "Sorry, you cannot edit another users profile "
