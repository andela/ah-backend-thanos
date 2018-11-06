import re
from rest_framework.exceptions import NotAcceptable


class Validator():

    def starts_with_letter(field, value):
        if re.compile("[a-zA-Z]+").match(value):
            return value
        else:
            raise NotAcceptable(
                detail=field + " Must start with a letter",
                code=406
                )
