from rest_framework import status
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
