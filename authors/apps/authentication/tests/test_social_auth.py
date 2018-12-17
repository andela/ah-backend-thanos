from rest_framework import status
from authors.apps.authentication.views import RegisterReturnUser
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from .basetest import BaseTestCase


User = get_user_model()


class SocialAuthApiTestCase(BaseTestCase):

    def test_invalid_social_provider(self):
        social_auth_Provider = "Instagram"
        url = reverse("authentication:oauth-singIn",
                      args=(social_auth_Provider,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_social_provider_google(self):
        social_auth_Provider = "google"
        url = reverse("authentication:oauth-singIn",
                      args=(social_auth_Provider,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_social_provider_twitter(self):
        social_auth_Provider = "twitter"
        url = reverse("authentication:oauth-singIn",
                      args=(social_auth_Provider,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_social_provider_facebook(self):
        social_auth_Provider = "facebook"
        url = reverse("authentication:oauth-singIn",
                      args=(social_auth_Provider,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_google_auth_invalid_token(self):
        access_token = "rwteyHUDUYWGbcwi34567283jdk34cwen"
        url = reverse("authentication:google-auth", args=(access_token,))
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_facebook_auth_invalid_token(self):
        access_token = "rwteyHUDUYWGbcwi34567283jdk34cwen"
        url = reverse("authentication:facebook-auth", args=(access_token,))
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_twitter_auth_invalid_token(self):
        access_key = "0000000000000000000000000000"
        access_secret = "0000000000000000000000000000000"
        url = reverse("authentication:twitter-auth",
                      args=(access_key, access_secret,))
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_Register_social_auth_user(self):
        email = "testingauth@gmail.com",
        username = "authTest",
        user = User.objects.get(email="daniel@test.com")
        response = RegisterReturnUser(user, email, username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = RegisterReturnUser(
            user=None, email=email, username=username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
