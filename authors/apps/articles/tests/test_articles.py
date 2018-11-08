from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth import get_user_model

from authors.apps.articles.models import Article
from authors.apps.core.utils.user_management import validate_author
from .Basetest import BaseTest

User = get_user_model()
articles_url = reverse("articles:list_create")
signup_url = reverse("authentication:signup")
login_url = reverse("authentication:login")


class ArticleTests(BaseTest):

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
        self.assertEqual(len(articles), 2)

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
        response = self.client.put("/api/articles/100000",
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

    def test_delete_article_not_found(self):
        self.test_create_article()
        response = self.client.delete("/api/articles/{}".format(100),
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Article Not found", str(response.data))

    def test_get_article_title(self):
        """ Test model method to get article title """
        self.title = self.data["title"]
        title = self.title.__str__()
        self.assertEqual(title, "How to train your Dragon")

    def test_validate_author(self):
        """Test that user can be registered as a super user"""
        self.assertRaises(AuthenticationFailed, lambda: validate_author(
            author_id="superuser", current_user_id=self.client.credentials))

    def test_invalid_page_number(self):
        self.test_create_article()
        articles_url = '/api/articles/?page=3'
        response = self.client.get(articles_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_page_number(self):
        self.test_create_article()
        articles_url = '/api/articles/?page=1'
        response = self.client.get(articles_url, format='json')

    def test_like_article(self):
        self.test_create_article()
        article = Article.objects.all().first()
        like_status_url = "/api/articles/{}/like_status".format(article.pk)
        response = self.client.post(like_status_url,
                                    self.like_status_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_status_article_doesent_exist(self):
        like_status_url = "/api/articles/{}/like_status".format(100)
        response = self.client.post(like_status_url,
                                    self.like_status_data,
                                    format='json')
        self.assertIn("Article Not found",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_already_like_article(self):
        self.test_create_article()
        article = Article.objects.all().first()
        like_status_url = "/api/articles/{}/like_status".format(article.pk)
        self.client.post(like_status_url,
                         self.like_status_data,
                         format='json')
        response = self.client.post(like_status_url,
                                    self.like_status_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_get_like_status(self):
        self.test_create_article()
        article = Article.objects.all().first()
        like_status_url = "/api/articles/{}/like_status".format(article.pk)
        self.client.post(like_status_url,
                         self.like_status_data,
                         format='json')
        response = self.client.get(like_status_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_like_status_article_doesnt_exist(self):
        like_status_url = "/api/articles/{}/like_status".format(100)
        self.client.post(like_status_url,
                         self.like_status_data,
                         format='json')
        response = self.client.get(like_status_url, format='json')
        self.assertIn("Article Not found",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_like_status_article_not_liked_yet(self):
        self.test_create_article()
        article = Article.objects.all().first()
        like_status_url = "/api/articles/{}/like_status".format(article.pk)
        response = self.client.get(like_status_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This article has not been liked/disliked yet",
                      str(response.data))

    def test_update_like_status(self):
        self.test_create_article()
        article = Article.objects.all().first()
        like_status_url = "/api/articles/{}/like_status".format(article.pk)
        like_status_update_url = "/api/articles/{}/like_status_update".format(
            article.pk)
        self.client.post(like_status_url,
                         self.like_status_data,
                         format='json')
        response = self.client.put(like_status_update_url,
                                   self.like_status_update_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
