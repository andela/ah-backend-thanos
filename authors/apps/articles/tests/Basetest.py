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


class BaseTest(APITestCase):

    def setUp(self):
        self.data = {
            "id": 1,
            "title": "How to train your Dragon",
            # "slug": "How to train your Dragon",
            "description": "Ever wonder how?",
            "body": "It takes a Jacobian",
            "image_url": "http://iviidev.info/downloads/image.jpg",
            "tag_list": ["dragons", "fantacy"]
        }
        self.wrong_data = {
            "id": 7,
            "title": "How to train your Dragon",
            # "slug": "How to train your Dragon",
            "description": "Ever wonder how?",
            "body": "It takes a Jacobian",
            "image_url": "http://iviidev.info/downloads/image.jpg",
            "tag_list": ["dragons", "fantacy"]
        }
        self.article_with_missing_fields = {
            "title": "Getting started with JS"
        }
        self.article_with_bad_title = {
            "title": "1",
            "description": "Ever wonder how?",
            "body": "It takes a Jacobian",
            "image_url": "http://iviidev.info/downloads/image.jpg",
            "tag_list": ["dragons", "fantacy"]
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
        self.edit_data = {
            "title": "This title has been edited",
        }
        self.like_status_data = {
            "like_status": "like"
        }
        self.like_status_update_data = {
            "like_status": "dislike"
        }
        self.comment_data = {
            "comments": {
                "comment_body": "This is a comment"
            }
        }

        self.thread_data = {
            "threads": {
                "thread_body": "This is a thread comment"
            }
        }
        self.user2_signup_data = {
            "user": {
                "email": "josekizito@gmail.com",
                "username": "josekizito",
                "password": "josekizito#1",
            }

        }
        self.user2_login_data = {
            "user": {
                "email": "josekizito@gmail.com",
                "password": "josekizito#1",
            }

        }

        # article rating
        self.article_score = {
            "rating": 5
        }

        self.out_of_range = {
            "rating": 6
        }

        self.response = self.client.post(
            signup_url, self.signup_data, format="json")

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

        self.res = self.client.post(articles_url, self.data, format='json')
        a_id = self.res.data['id']
        self.url = reverse("articles:comment_on_article",
                           args=(a_id,))
        self.comment_res = self.client.post(self.url, self.comment_data,
                                            format='json')
        c_id = self.comment_res.data['id']
        self.single_comm_url = reverse("articles:comment_by_id",
                                       args=(a_id, c_id,))
        self.thread_url = reverse("articles:comment_on_comment",
                                  args=(a_id, c_id,))
