import re
from rest_framework.serializers import ValidationError


class Validator():

    def starts_with_letter(field, value):
        if re.compile("[a-zA-Z]+").match(value):
            return value
        else:
            raise ValidationError(
                detail=field + " Must start with a letter",
                code=400
                )
