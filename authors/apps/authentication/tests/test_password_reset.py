
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from .basetest import BaseTestCase
from rest_framework import status
import jwt

User = get_user_model()
signup_url = reverse("authentication:signup")
login_url = reverse("authentication:login")
url_password_reset_email = reverse("authentication:reset_password_email")


class UserApiTestCase(BaseTestCase):

    def test_password_reset(self):

        # password reset
        response_reset_password = self.client.put(
            self.url_reset_password, self.reset_password_data, format="json")
        self.assertEqual(
            response_reset_password.data, {
                "message": "your has successfully changed your password"
            }
        )

    def test_password_reset_send_email(self):

        # password reset send email
        response_reset_password = self.client.post(
            url_password_reset_email,
            self.reset_password_send_email_data,
            format="json")
        self.assertEqual(response_reset_password.status_code,
                         status.HTTP_200_OK)

    def test_password_reset_send_email_email_doesnt_exist(self):

        # password reset send email
        response_reset_password_wrong_data = self.client.post(
            url_password_reset_email,
            self.reset_password_wrong_email_data,
            format="json")
        self.assertEqual(response_reset_password_wrong_data.data,
                         {"error": "User with that email does not exist"})

    def test_password_reset_donot_match(self):

        # password reset with data that does not match
        response_reset_password = self.client.put(
            self.url_reset_password,
            self.reset_password_unmatching_data,
            format="json")
        self.assertEqual(
            response_reset_password.data, {
                "error": "The passwords do not match"
            }
        )

    def test_password_reset_invalid_data(self):

        # password reset with invalid input data
        response_reset_password = self.client.put(
            self.url_reset_password,
            self.reset_password_unvalid_data,
            format="json")
        self.assertEqual(
            response_reset_password.data, {
                "error": "Ensure your password is alphanumeric, with Minimum eight characters, at least one letter, one number and one special character"
            }
        )
