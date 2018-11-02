
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status
from rest_framework.serializers import ValidationError

from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from ..validators import is_profile_valid


User = get_user_model()

signup_url = reverse("authentication:signup")
login_url = reverse("authentication:login")
profiles_url = reverse("profiles:profile_list")


class ProfileApiTestCase(APITestCase):
    def setUp(self):
        self.unauth = APIClient()
        self.factory = APIRequestFactory()

        self.user_data = {
            "user": {
                "username": "bruce",
                "email": "bruce@gmail.com",
                "password": "brucesama#1"
            }
        }
        self.user_data2 = {
            "user": {
                "username": "jemimah",
                "email": "jemimah@gmail.com",
                "password": "brucesama#1"
            }
        }

        self.login_data = {
            "user": {
                "email": "bruce@gmail.com",
                "password": "brucesama#1",
            }
        }
        self.profile_data = {
            "profiles": {
                "username": "bruce",
                "bio": "this is a test user",
                "image": "",
                "last_name": "",
                "first_name": ""
            }
        }

        self.edit_profile_data = {
            "profiles": {
                "username": "jemimah",
                "bio": "this is a test user",
                "image": "",
                "last_name": "",
                "first_name": ""
            }
        }

        self.validated_profile_data = {
            "profiles": {
                "username": "!@#$$",
                "bio": "!@@##$",
                "image": "",
                "last_name": "",
                "first_name": ""
            }
        }

        self.edited_profile_data = {
            "profiles": {
                "username": "bruce",
                "bio": "this is edited",
                "image": "",
                "last_name": "Mars",
                "first_name": "Bruce"
            }
        }

        self.client.post(signup_url, self.user_data, format='json')
        self.client.post(signup_url, self.user_data2, format='json')
        user = User.objects.get(email=self.login_data["user"]["email"])
        uid = force_text(urlsafe_base64_encode(user.email.encode("utf8")))
        username = self.profile_data["profiles"]["username"]
        activation_token = default_token_generator.make_token(user)
        self.profile_url = reverse("profiles:profile", args=(username,))
        url = reverse("authentication:activate_account",
                      args=(uid, activation_token,))
        self.client.get(url, format="json")

        self.response = self.client.post(
            login_url, self.login_data, format='json')
        token = self.response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_user_already_exists(self):
        response = self.client.post(
            signup_url, self.user_data,  format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_retrieval(self):
        """Test whether the profile has been created"""
        user = self.user_data["user"]["username"]
        response = self.client.get(
            self.profile_url,  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['username']), user)

    def test_user_views_all_profiles(self):
        """Test whether user can view all the other profiles"""
        response = self.client.get(profiles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_url_is_authenticated(self):
        """Test whether request is authenticated"""
        response = self.unauth.get('/api/profiles', self.profile_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_profile(self):
        """Test whether profile can be edited"""
        response = self.client.put(
            self.profile_url,
            self.edited_profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            self.edited_profile_data['profiles']['bio'], response.data['bio'])

    def test_validate_profile(self):
        """Test whether profile is validated"""
        with self.assertRaises(ValidationError):
            is_profile_valid(self, last_name='!@##$',
                             bio='!@###$', first_name='!@@#')

    def test_profile_update(self):
        """Tests that a profile can be updated by a user"""
        response = self.client.put(
            self.profile_url, data=self.edit_profile_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            self.profile_data['profiles']['username'],
            response.data['username']
        )
        self.assertIn(
            self.profile_data['profiles']['bio'], response.data['bio']
        )
        self.assertIn(
            self.profile_data['profiles']['image'], response.data['image']
        )

    def test_cannot_edit_another_profile(self):
        """Test whether a user cannot test another's profile"""
        username = "jemimah"
        profile_url = reverse("profiles:profile", args=(username,))
        response = self.client.put(profile_url, self.edit_profile_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_found(self):
        """Test whether a user cannot test another's profile"""
        username = "sulaiman"
        profile_url = reverse("profiles:profile", args=(username,))
        response = self.client.put(profile_url, self.edit_profile_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
