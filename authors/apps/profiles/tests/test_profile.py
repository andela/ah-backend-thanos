from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from rest_framework.serializers import ValidationError

from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from ..validators import is_profile_valid
from authors.apps.core.utils.userbasetest import UserBaseTestCase


User = get_user_model()

signup_url = reverse("authentication:signup")
login_url = reverse("authentication:login")
profiles_url = reverse("profiles:profile_list")


class ProfileApiTestCase(UserBaseTestCase):
    def setUp(self):
        super(ProfileApiTestCase, self).setUp()  # call setup from super

        self.unauth = APIClient()
        self.factory = APIRequestFactory()

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

        self.client.post(signup_url, self.signup_data, format='json')
        self.client.post(signup_url, self.signup_data_user2, format='json')
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
            signup_url, self.signup_data,  format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_retrieval(self):
        """Test whether the profile has been created"""
        user = self.signup_data["user"]["username"]
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
            is_profile_valid(self, last_name='!@###$',
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
        self.assertIn("Sorry, you cannot edit another users profile",
                      str(response.data))

    def test_user_not_found(self):
        """Test whether a user cannot test another's profile"""
        username = "sulaiman"
        profile_url = reverse("profiles:profile", args=(username,))
        response = self.client.put(profile_url, self.edit_profile_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_another_user(self):
        """Test whether user A (current user) can follow user B"""
        user_b = User.objects.all().last()
        res = self.client.post("/api/users/{}/follow".format(user_b.id),
                               {},
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("jemimah", str(res.data))

    def test_follow_oneself(self):
        """Test whether user A (current user) can follow themselves"""
        user_a = User.objects.all().first()
        res = self.client.post("/api/users/{}/follow".format(user_a.id),
                               {},
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The current user is the same as the selected user",
                      str(res.data))

    def test_follow_another_user_twice(self):
        """Test wheter user A (current) can follow user B twice"""
        self.test_follow_another_user()
        user_b = User.objects.all().last()
        res = self.client.post("/api/users/{}/follow".format(user_b.id),
                               {},
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You are already following this user",
                      str(res.data))

    def test_follow_inexistent_user(self):
        """Test whether user A (current) can follow ghost user 999999"""
        res = self.client.post("/api/users/{}/follow".format(999999),
                               {},
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("User Not found", str(res.data))

    def test_unfollow_user(self):
        """Test whether wheter user A (current) can unfollow user B"""
        self.test_follow_another_user()
        user_b = User.objects.all().last()
        res = self.client.delete("/api/users/{}/follow".format(user_b.id),
                                 format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("You have Unfollowed the User", str(res.data))

    def test_unfollow_user_twice(self):
        """Test whether user A (current) can Unfollow user B twice"""
        self.test_unfollow_user()
        user_b = User.objects.all().last()
        res = self.client.delete("/api/users/{}/follow".format(user_b.id),
                                 format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("You are currently not following this user",
                      str(res.data))

    def test_unfollow_inexistent_user(self):
        """Test whether user A (current) can Unfollow a ghost user 999999"""
        res = self.client.delete("/api/users/{}/follow".format(999999),
                                 format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("User Not found", str(res.data))

    def test_get_followees_when_not_present(self):
        """
        Test whether user A can get a list of users
        he/she is following, when they haven't followed anyone
        """
        user_b = User.objects.all().last()
        res = self.client.get(
            "/api/users/{}/following".format(user_b.id),
            format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("This user is not following anyone", str(res.data))

    def test_get_followers_when_not_present(self):
        """
        Test whether user A can get a list of followers,
        when there are no followers
        """
        user_a = User.objects.all().first()
        res = self.client.get(
            "/api/users/{}/followers".format(user_a.id),
            format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("This user is not being followed by anyone",
                      str(res.data))
