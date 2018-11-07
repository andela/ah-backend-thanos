from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()
articles_url = reverse("articles:list_create")
signup_url = reverse("authentication:signup")
login_url = reverse("authentication:login")


class UserBaseTestCase(APITestCase):

    def setUp(self):
        self.signup_data = {
            "user": {
                "username": "bruce",
                "email": "bruce@gmail.com",
                "password": "password123#"
            }
        }
        self.login_data = {
            "user": {
                "email": "bruce@gmail.com",
                "password": "password123#",
            }
        }
        self.signup_data_user2 = {
            "user": {
                "username": "jemimah",
                "email": "jemimah@gmail.com",
                "password": "password123#"
            }
        }
        self.login_data_user2 = {
            "user": {
                "email": "jemimah@gmail.com",
                "password": "password123#",
            }
        }

        self.register_user(self.signup_data)
        self.verify_user(self.login_data)
        self.user_login(self.login_data)

        self.register_user(self.signup_data_user2)
        self.verify_user(self.login_data_user2)
        self.user_login(self.login_data_user2)

    # Register Users
    def register_user(self, data_passed):
        self.response = self.client.post(signup_url,
                                         data_passed,
                                         format="json")

    # Verify user accounts
    def verify_user(self, data_passed):
        user = User.objects.get(email=data_passed["user"]["email"])
        uid = force_text(urlsafe_base64_encode(user.email.encode("utf8")))
        activation_token = default_token_generator.make_token(user)
        url = reverse("authentication:activate_account",
                      args=(uid, activation_token,))
        self.client.get(url, format="json")  # toggle link to verify

    # User login
    def user_login(self, data_passed):
        self.login_response = self.client.post(
            login_url, data_passed, format="json")
        self.assertEqual(self.login_response.status_code, status.HTTP_200_OK)
        login_token = self.login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + login_token)
