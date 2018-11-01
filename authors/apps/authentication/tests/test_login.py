from rest_framework import status, exceptions
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

from ..backends import JWTAuthentication

from .basetest import BaseTestCase

User = get_user_model()
signup_url = reverse("authentication:signup")
login_url = reverse("authentication:login")


class UserApiTestCase(BaseTestCase):

    def test_login_user(self):

        # Test user login
        self.login_response = self.client.post(
            login_url, self.login_data, format="json")
        self.assertEqual(self.login_response.status_code, status.HTTP_200_OK)
        login_token = self.login_response.data['token']
        self.assertEqual(
            self.login_response.data, {"email": "daniel@test.com",
                                       "username": "daniel",
                                       "token": login_token}
        )

    def test_get_user_email(self):
        self.user = self.login_data["user"]["email"]
        """ Test model method to get user's email """
        email = self.user.__str__()
        self.assertEqual(email, "daniel@test.com")
