import re

from rest_framework import serializers


def is_profile_valid(self, bio, last_name, first_name):
    """This function contains the validations for the profile"""

    if re.compile('[!@#$%^&*:;?><.]').match(bio):
        raise serializers.ValidationError(
            {'bio':
             'Must start with a letter'}
        )

    if re.compile('[!@#$%^&*:;?><.]').match(first_name):
        raise serializers.ValidationError(
            {'last_name':
             'Must start with a letter'}
        )

    if re.compile('[!@#$%^&*:;?><.]').match(last_name):
        raise serializers.ValidationError(
            {'Must start with a letter'}
        )
