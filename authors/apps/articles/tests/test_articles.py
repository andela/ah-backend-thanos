from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.exceptions import AuthenticationFailed
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

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

    def test_get_two_articles(self):
        # first create an article
        self.test_create_article()
        self.test_create_article()
        articles = Article.objects.all()
        response = self.client.get(articles_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(articles), 3)

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_article_not_found(self):
        response = self.client.put("/api/articles/2",
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
        response = self.client.delete("/api/articles/{}".format(100),
                                      format='json')
        self.assertIn("Article Not found", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
        articles_url = '/api/articles?page=999'
        response = self.client.get(articles_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_page_number(self):
        self.test_create_article()
        articles_url = '/api/articles?page=1'
        self.client.get(articles_url, format='json')

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
        like_status_update_url = "/api/articles/{}/like_status".format(
            article.pk)
        self.client.post(like_status_url,
                         self.like_status_data,
                         format='json')
        response = self.client.put(like_status_update_url,
                                   self.like_status_update_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_rates_own_article(self):
        self.test_create_article()
        self.client.post(signup_url,
                         self.user2_signup_data,
                         format="json")
        user = User.objects.get(email=self.user2_login_data["user"]["email"])
        uid = force_text(urlsafe_base64_encode(user.email.encode("utf8")))
        activation_token = default_token_generator.make_token(user)
        url = reverse("authentication:activate_account",
                      args=(uid, activation_token,))
        self.client.get(url, format="json")

        login_response1 = self.client.post(
            login_url, self.user2_login_data, format="json")
        login_token = login_response1.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + login_token)
        self.client.post(articles_url, self.data, format='json')

        response = self.client.get(articles_url, self.data, format='json')
        article = response.json()['results'][0]

        response = self.client.post("/api/articles/{}/rating".format(
            article['id']),
            self.article_score, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_rates_an_article_twice(self):
        self.client.post(signup_url,
                         self.user2_signup_data,
                         format="json")
        user = User.objects.get(email=self.user2_login_data["user"]["email"])
        uid = force_text(urlsafe_base64_encode(user.email.encode("utf8")))
        activation_token = default_token_generator.make_token(user)
        url = reverse("authentication:activate_account",
                      args=(uid, activation_token,))
        self.client.get(url, format="json")

        login_response = self.client.post(
            login_url, self.user2_login_data, format="json")
        login_token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + login_token)

        query_data = self.client.get(articles_url, format='json')
        article = query_data.json()['results'][0]
        self.client.post("/api/articles/{}/rating".format(article['id']),
                         self.article_score, format='json')
        response = self.client.post("/api/articles/{}/rating".format(
            article['id']),
            self.article_score, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You already rated this article",
                      response.data['detail'])

    def test_score_out_of_range(self):
        query_data = self.client.get(articles_url, self.data, format='json')
        article = query_data.json()['results'][0]
        response = self.client.post("/api/articles/{}/rating".format(
            article['id']),
            self.out_of_range, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Score value must be between `0` and `5`",
            response.data['detail'])

    def test_favorite_article(self):
        self.test_create_article()
        article = Article.objects.all().first()
        favorite_status_url = "/api/articles/{}/favorite_status"\
                              .format(article.pk)
        response = self.client.post(favorite_status_url,
                                    self.favorite_status_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_favorite_articles(self):
        self.test_create_article()
        article = Article.objects.all().first()
        favorite_status_url = "/api/articles/{}/favorite_status"\
                              .format(article.pk)
        response = self.client.post(favorite_status_url,
                                    self.favorite_status_data,
                                    format='json')
        favorite_status_url = "/api/articles/favorites/"
        response = self.client.get(favorite_status_url,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_favorite_status_article_doesent_exist(self):
        favorite_status_url = "/api/articles/{}/favorite_status".format(100)
        response = self.client.post(favorite_status_url,
                                    self.favorite_status_data,
                                    format='json')
        self.assertIn("Article Not found",
                      str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_already_favorited_article(self):
        self.test_create_article()
        article = Article.objects.all().first()
        favorite_status_url = "/api/articles/{}/favorite_status"\
                              .format(article.pk)
        self.client.post(favorite_status_url,
                         self.favorite_status_data,
                         format='json')
        response = self.client.post(favorite_status_url,
                                    self.favorite_status_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_get_favorite_status(self):
        self.test_create_article()
        article = Article.objects.all().first()
        favorite_status_url = "/api/articles/{}/favorite_status"\
                              .format(article.pk)
        self.client.post(favorite_status_url,
                         self.favorite_status_data,
                         format='json')
        response = self.client.get(favorite_status_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_favorite_status_article_doesnt_exist(self):
        favorite_status_url = "/api/articles/{}/favorite_status".format(100)
        self.client.post(favorite_status_url,
                         self.favorite_status_data,
                         format='json')
        response = self.client.get(favorite_status_url, format='json')
        self.assertIn("Article Not found", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_favorite_status_article_not_liked_yet(self):
        self.test_create_article()
        article = Article.objects.all().first()
        favorite_status_url = "/api/articles/{}/favorite_status".format(
            article.pk)
        response = self.client.get(favorite_status_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This article has not been favorited yet",
                      str(response.data))

    def test_update_favorite_status(self):
        self.test_create_article()
        article = Article.objects.all().first()
        favorite_status_url = "/api/articles/{}/favorite_status"\
                              .format(article.pk)
        favorite_status_update_url = "/api/articles/{}/favorite_status"\
                                     .format(article.pk)
        self.client.post(favorite_status_url,
                         self.favorite_status_data,
                         format='json')
        response = self.client.put(favorite_status_update_url,
                                   self.favorite_status_update_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_favorite_status_article_doesnt_exist(self):
        favorite_status_update_url = "/api/articles/{}/favorite_status"\
                                     .format(100)
        response = self.client.put(favorite_status_update_url,
                                   self.favorite_status_update_data,
                                   format='json')
        self.assertIn("Article Not found", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_all_tags(self):
        """Test whether one can get a list of tags"""
        self.test_create_article()
        response = self.client.get("/api/tags", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("fantacy", str(response.data))

    def search_articles_by_title(self):
        self.test_create_article()
        response = self.client.get("/api/articles?title=dragon", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("How to train your Dragon", str(response.data))

    def search_articles_by_author(self):
        self.test_create_article
        response = self.client.get(
            "/api/articles?author={}".format(User.objects.all().first()),
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("How to train your Dragon", str(response.data))
