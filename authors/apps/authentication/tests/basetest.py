from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
import jwt
from datetime import datetime, timedelta
from django.conf import settings

User = get_user_model()


class BaseTestCase(APITestCase):

    def setUp(self):
        self.user_data = {
            "user": {
                "email": "judeinn@gmail.com",
                "username": "jude",
                "password": "testpassword#123"
            }
        }
        self.invalid_email_data = {
            "user": {
                "email": "test@testcom",
                "username": "testuser",
                "password": "testpassword1"
            }
        }
        self.invalid_username = {
            "user": {
                "email": "judeinn@gmail.com",
                "username": "<@#!$%^$^",
                "password": "testpassword"
            }
        }
        self.invalid_pass_data = {
            "user": {
                "email": "judeinn@gmail.com",
                "username": "testuser",
                "password": "123345678"
            }
        }
        self.pass_less8_data = {
            "user": {
                "email": "judeinn@gmail.com",
                "username": "testuser",
                "password": "12345l",
            }
        }
        self.alp_pass_data = {
            "user": {
                "username": "jude",
                "email": "judeinn@gmail.com",
                "password": "judesecret"
            }
        }

        self.no_fields = {
            "user": {
                "username": "",
                "email": "",
                "password": "judesecret"
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
        self.login_data = {
            "user": {
                "email": "daniel@test.com",
                "password": "testpassword#123",
            }
        }

        self.password_reset_payload = {
            "email": "daniel@test.com"
        }

        self.password_reset_payload_no_redirect = {"email": "daniel@test.com",}

        self.reset_password_data = {
            "new_password": "password1234@",
            "confirm_password": "password1234@"
        }

        self.reset_password_unmatching_data = {
            "new_password": "password1234@",
            "confirm_password": "password1234"
        }

        self.reset_password_unvalid_data = {
            "new_password": "password1234",
            "confirm_password": "password1234"
        }

        # Register User
        self.create_user = User(username="daniel",
                                email="daniel@test.com"
                                )
        self.create_user.set_password("testpassword#123")
        self.create_user.save()

        #  Verify user account
        user = User.objects.get(email=self.login_data["user"]["email"])
        uid = force_text(urlsafe_base64_encode(user.email.encode("utf8")))
        activation_token = default_token_generator.make_token(user)
        url = reverse("authentication:activate_account",
                      args=(uid, activation_token,))
        self.client.get(url, format="json")

        # password reset token generation and passing in the url
        email = self.password_reset_payload['email']
        dt = datetime.now()+timedelta(days=1)
        self.reset_password_token = jwt.encode({'email': email, 'exp': int(
            dt.strftime('%s'))}, settings.SECRET_KEY, 'HS256').decode('utf-8')
        self.url_reset_password = "/api/users/reset_password/{}".format(
            self.reset_password_token)
        self.reset_password_send_email_data = {"email": "daniel@test.com", "callback_url":"https://www.pivotaltracker.com/n/projects/2206434"}
        self.reset_password_wrong_email_data = {"email": "judesg@gmail.com"}

        self.subscribe_status_update_data = {"is_subscribed": "False"}
