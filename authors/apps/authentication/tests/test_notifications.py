from .basetest import BaseTestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()
login_url = reverse("authentication:login")


class NotificationsTestCase(BaseTestCase):

    def test_update_subscription_status(self):
        create_user = User(username="danielnuwa",
                           email="danielnuwa@test.com"
                           )
        create_user.set_password("testpassword#123")
        create_user.save()
        login_data = {"user": {"email": "danielnuwa@test.com",
                               "password": "testpassword#123"}}
        user = User.objects.get(email=login_data["user"]["email"])
        uid = force_text(urlsafe_base64_encode(user.email.encode("utf8")))
        activation_token = default_token_generator.make_token(user)
        url = reverse("authentication:activate_account",
                      args=(uid, activation_token,))
        self.client.get(url, format="json")
        user_id = User.objects.filter(email="danielnuwa@test.com")
        for user in user_id:
            user.id
        login_resp = self.client.post(
            login_url, login_data, format="json")
        login_token = login_resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + login_token)
        subscription_status_update_url = "/api/users/{}/unsubscribe"\
                                         .format(user.id)
        response = self.client.put(subscription_status_update_url,
                                   self.subscribe_status_update_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_subscription_status_invalid_user(self):
        create_user = User(username="danielnuwa",
                           email="danielnuwa@test.com"
                           )
        create_user.set_password("testpassword#123")
        create_user.save()
        login_data = {"user": {"email": "danielnuwa@test.com",
                               "password": "testpassword#123"}}
        user = User.objects.get(email=login_data["user"]["email"])
        uid = force_text(urlsafe_base64_encode(user.email.encode("utf8")))
        activation_token = default_token_generator.make_token(user)
        url = reverse("authentication:activate_account",
                      args=(uid, activation_token,))
        self.client.get(url, format="json")
        user_id = User.objects.filter(email="danielnuwa@test.com")
        for user in user_id:
            user.id
        login_resp = self.client.post(
            login_url, login_data, format="json")
        login_token = login_resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + login_token)
        subscription_status_update_url = "/api/users/{}/unsubscribe"\
                                         .format(40)
        response = self.client.put(subscription_status_update_url,
                                   self.subscribe_status_update_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
