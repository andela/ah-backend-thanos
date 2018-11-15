from rest_framework import status


from .Basetest import BaseTest


class ReportArticleTestCase(BaseTest):
    def test_share_email(self):
        """Test user can share an article by email"""
        self.client.post(self.url, self.comment_data,
                         format='json')
        response = self.client.post(
            self.share_email_url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_share_facebook(self):
        """Test user can share an article by facebook"""
        self.client.post(self.url, self.comment_data,
                         format='json')
        response = self.client.post(
            self.share_facebook_url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_share_twitter(self):
        """Test user can share an article by twitter"""
        self.client.post(self.url, self.comment_data,
                         format='json')
        response = self.client.post(
            self.share_twitter_url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
