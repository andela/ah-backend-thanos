from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from authors.apps.articles.models import Article

User = get_user_model()
articles_url = reverse("articles:list_create")
signup_url = reverse("authentication:signup")
login_url = reverse("authentication:login")


class ArticleTests(APITestCase):

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

    def test_create_article(self):
        response = self.client.post(articles_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("How to train your Dragon", str(response.data))

    def test_get_all_articles(self):
        # first create an article
        self.test_create_article()
        articles = Article.objects.all()
        response = self.client.get(articles_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("How to train your Dragon", str(response.data))
        self.assertEqual(len(articles), 1)

    def test_get_article_by_id(self):
        self.test_create_article()
        article = Article.objects.all().first()
        response = self.client.get("/api/articles/{}".format(article.pk),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("How to train your Dragon", str(response.data))

    def test_get_article_by_slug(self):
        self.test_create_article()
        article = Article.objects.all().first()
        response = self.client.get("/api/articles/{}".format(article.slug),
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("How to train your Dragon", str(response.data))

    def test_create_article_wrong_title(self):
        """
        Test creating an article with an erroneous title
        """
        response = self.client.post(articles_url,
                                    self.article_with_bad_title,
                                    format='json')
        self.assertIn("Must start with a letter", str(response.data))

    def test_create_article_missing_fields(self):
        """
        Test creating an article with missing fields
        """
        response = self.client.post(articles_url,
                                    self.article_with_missing_fields,
                                    format='json')
        self.assertIn("This field may not be null", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_article(self):
        self.test_create_article()
        article = Article.objects.all().first()
        response = self.client.put("/api/articles/{}".format(article.pk),
                                   self.edit_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("This title has been edited", str(response.data))

    def test_invalid_token(self):
        # set a wrong token and try to use it to create an article
        self.client.credentials(HTTP_AUTHORIZATION='Token VERY-WRONG-TOKEN')
        response = self.client.post(articles_url, self.data, format='json')
        self.assertIn("Invalid/expired token", str(response.data))

    def test_article_not_found(self):
        response = self.client.put("/api/articles/1",
                                   self.edit_data,
                                   format='json')
        self.assertIn("Article Not found", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_article(self):
        self.test_create_article()
        article = Article.objects.all().first()
        response = self.client.delete("/api/articles/{}".format(article.pk),
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Article deleted sucessfully", str(response.data))
