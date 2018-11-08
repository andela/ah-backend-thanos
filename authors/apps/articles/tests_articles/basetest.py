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


class BaseTestCase(APITestCase):

    def setUp(self):
        self.data = {
            "title": "How to train your Dragon",
            "description": "Ever wonder how?",
            "body": "It takes a Jacobian",
            "image_url": "http://iviidev.info/downloads/image.jpg",
            "tag_list": ["dragons", "fantacy"]
        }
        self.edit_data = {
            "title": "This title has been edited",
        }
        self.article_with_bad_title = {
            "title": "1",
            "description": "Ever wonder how?",
            "body": "It takes a Jacobian",
            "image_url": "http://iviidev.info/downloads/image.jpg",
            "tag_list": ["dragons", "fantacy"]
        }
        self.article_with_missing_fields = {
            "title": "Getting started with JS"
        }
        self.signup_data = {
            "user": {
                "email": "jackkatto@gmail.com",
                "username": "jackkatto",
                "password": "jackkatto123#",
            }
        }
        self.login_data = {
            "user": {
                "email": "jackkatto@gmail.com",
                "password": "jackkatto123#",
            }
        }
        self.favorite_status_data = {
            "favorite_status": "True"
        }
        self.favorite_status_update_data = {
            "favorite_status": "False"
        }
        # Register User
        self.response = self.client.post(signup_url,
                                         self.signup_data,
                                         format="json")
        #  Verify user account
        user = User.objects.get(email=self.login_data["user"]["email"])
        uid = force_text(urlsafe_base64_encode(user.email.encode("utf8")))
        activation_token = default_token_generator.make_token(user)
        url = reverse("authentication:activate_account",
                      args=(uid, activation_token,))
        self.client.get(url, format="json")
        # Test user login
        self.login_response = self.client.post(
            login_url, self.login_data, format="json")
        self.assertEqual(self.login_response.status_code, status.HTTP_200_OK)
        login_token = self.login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + login_token)
