from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from .basetest import BaseTestCase
from rest_framework import status

User = get_user_model()
signup_url = reverse("authentication:signup")
login_url = reverse("authentication:login")
url_password_reset_email = reverse("authentication:reset_password_email")


class UserApiTestCase(BaseTestCase):

    def test_password_reset(self):

        # password reset
        response_reset_password = self.client.put(
            self.url_reset_password, self.reset_password_data, format="json")
        self.assertIn("you have successfully changed your password",
                      str(response_reset_password.data))
        self.assertEqual(response_reset_password.status_code,
                         status.HTTP_200_OK)

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
        self.assertIn("User with that email does not exist",
                      str(response_reset_password_wrong_data.data))
        self.assertEqual(response_reset_password_wrong_data.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_redirect_url_is_not_provided(self):
        response_reset_password = self.client.post(
            url_password_reset_email,
			self.password_reset_payload_no_redirect,
			format="json")
        self.assertIn(
			"Please supply the callback url", str(response_reset_password.data)
		)
        self.assertEqual(response_reset_password.status_code,
						status.HTTP_400_BAD_REQUEST)


    def test_password_reset_donot_match(self):

        # password reset with data that does not match
        response_reset_password = self.client.put(
            self.url_reset_password,
            self.reset_password_unmatching_data,
            format="json")
        self.assertIn(
            "The passwords do not match", str(response_reset_password.data)
        )
        self.assertEqual(response_reset_password.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_password_reset_invalid_data(self):

        # password reset with invalid input data
        response_reset_password = self.client.put(
            self.url_reset_password,
            self.reset_password_unvalid_data,
            format="json")
        self.assertIn(
            "Ensure your password is alphanumeric, with Minimum eight characters, at least one letter, one number and one special character",
            str(response_reset_password.data)
        )
        self.assertEqual(response_reset_password.status_code,
                         status.HTTP_400_BAD_REQUEST)
