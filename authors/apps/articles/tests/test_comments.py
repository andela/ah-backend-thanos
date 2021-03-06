from rest_framework.reverse import reverse
from rest_framework import status
from authors.apps.articles.models import Article, Comment

from .Basetest import BaseTest


articles_url = reverse("articles:list_create")
a_id = 100
bkmk_url = reverse("articles:create_bookmark", args=(a_id,))


class ArticleTests(BaseTest):
    def test_create_comment(self):
        """Test user can create a comment"""
        response = self.client.post(self.url, self.comment_data,
                                    format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)

    def test_get_comments(self):
        """Test user can get a comment"""
        self.client.post(self.url, self.comment_data,
                         format='json')
        response = self.client.get(self.url,
                                   format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_article_exists(self):
        """Test article exists"""
        self.res = self.client.post(
            articles_url, self.data, format='json')
        response = self.client.post('/api/articles/90/comments',
                                    self.comment_data,
                                    format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_get_comment_body(self):
        """ Test model method to get comment body """
        self.comment_body = self.comment_data["comments"]["comment_body"]
        comment = self.comment_body.__str__()
        self.assertEqual(comment, "This is a comment")

    def test_article_not_found(self):
        """Test article are not found"""
        response = self.client.get("/api/articles/110/comments",
                                   self.data,
                                   format='json')
        self.assertIn("Sorry this article doesn\'t exist",
                      str(response.data))
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_get_thread(self):
        """ Test model method to get thread body """
        self.thread = self.thread_data["threads"]["thread_body"]
        thread = self.thread.__str__()
        self.assertEqual(thread, "This is a thread comment")

    def test_create_thread(self):
        """Test whether a thread comment is created"""
        response = self.client.post(self.thread_url,
                                    self.thread_data,
                                    format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)

    def test_get_threads(self):
        """Test whether thread comments are returned"""
        self.client.post(self.thread_url,
                         self.thread_data,
                         format='json')
        response = self.client.get(self.thread_url,
                                   self.thread_data,
                                   format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_comment_not_found(self):
        """Test whether a comment is not found"""
        response = self.client.post("/api/articles/11/comments/999/threads",
                                    self.thread_data,
                                    format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertIn('Not found', str(response.data))

    def test_bookmark_not_found(self):
        """Test whether a article is not found for a bookmark"""
        response = self.client.post('api/articles/{}/bookmarks'.format(1000),
                                    format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_delete_comment(self):
        self.test_create_comment()
        response = self.client.delete(self.single_comm_url,
                                      format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
        self.assertIn("Comment deleted sucessfully", str(response.data))

    def test_can_bookmark_article(self):
        """Test if the article has been bookmarked"""
        self.res = self.client.post(
            self.url, self.data, format='json')
        result = self.client.post(self.bookmark_url, format="json")
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_get_bookmark(self):
        """Test if the article has been bookmarked"""
        self.res = self.client.post(
            self.url, self.data, format='json')
        self.client.post(self.bookmark_url, format="json")
        result = self.client.get(self.bookmark_url, format="json")
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_delete_bookmark(self):
        """Test if the bookmark can be deleted"""
        self.test_can_bookmark_article()
        result = self.client.delete(self.unbookmark_url, format='json')
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn("Bookmark succesfully deleted", str(result.data))

    def test_no_comments_for_article(self):
        """Test no comments for a specific article"""
        article = {
            "title": "How to train your Dog",
            "description": "Ever wonder how?",
            "body": "It takes a Jacobian",
            "image_url": "http://iviidev.info/downloads/image.jpg",
            "tag_list": ["dragons", "fantacy"]
        }
        self.client.post(articles_url, article, format='json')
        result = self.client.get(
            '/api/articles/{}/comments'.format(
                Article.objects.all().first().id),
            format='json')
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Sorry there are no comments for this article",
                      str(result.data))

    def test_like_comment(self):
        articles_url = reverse("articles:list_create")
        self.client.post(articles_url, self.data, format='json')
        self.client.post(self.url, self.comment_data, format='json')
        article = Article.objects.all().first()
        comment = Comment.objects.all().first()
        article_id = article.id
        comment_id = comment.id
        like_status_url = reverse("articles:like_comment",
                                  args=(article_id, comment_id,))
        response = self.client.post(like_status_url,
                                    self.like_status_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_comment_like(self):
        articles_url = reverse("articles:list_create")
        self.client.post(articles_url, self.data, format='json')
        self.client.post(self.url, self.comment_data, format='json')
        article = Article.objects.all().first()
        comment = Comment.objects.all().first()
        article_id = article.id
        comment_id = comment.id
        like_status_url = reverse(
            "articles:like_comment", args=(article_id, comment_id,))
        response = self.client.get(like_status_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unlike_comment(self):
        articles_url = reverse("articles:list_create")
        self.client.post(articles_url, self.data, format='json')
        self.client.post(self.url, self.comment_data, format='json')
        article = Article.objects.all().first()
        comment = Comment.objects.all().first()
        article_id = article.id
        comment_id = comment.id
        like_status_url = reverse(
            "articles:like_comment", args=(article_id, comment_id,))
        self.client.post(like_status_url,
                         self.like_status_data,
                         format='json')
        response = self.client.post(like_status_url,
                                    self.like_status_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_change_like_comment_status(self):
        articles_url = reverse("articles:list_create")
        self.client.post(articles_url, self.data, format='json')
        self.client.post(self.url, self.comment_data, format='json')
        article = Article.objects.all().first()
        comment = Comment.objects.all().first()
        article_id = article.id
        comment_id = comment.id
        like_status_url = reverse(
            "articles:like_comment", args=(article_id, comment_id,))
        self.client.post(like_status_url,
                         self.like_status_data,
                         format='json')
        response = self.client.post(like_status_url,
                                    self.like_status_update_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
