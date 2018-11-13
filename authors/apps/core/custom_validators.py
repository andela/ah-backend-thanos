from rest_framework.serializers import ValidationError
import re


class ValidateUserData:

    def reg_fields_validation(self, username, email, password):

        if re.compile('[!@#$%^&*:;?><.0-9]').match(username):
            raise ValidationError(
                "Invalid Username , it contains invalid characters."
            )

        msg = "Ensure password is alphanumeric, with a special character"
        ex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$'
        if (re.compile(ex).search(password) is None):
            raise ValidationError(msg)

    def starts_with_letter(self, field, value):
        if re.compile("[a-zA-Z]+").match(value):
            return value
        else:
            raise ValidationError(
                detail=field + " Must start with a letter",
                code=400
            )
