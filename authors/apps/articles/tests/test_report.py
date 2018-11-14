from rest_framework import status


from .Basetest import BaseTest


class ReportArticleTestCase(BaseTest):
    def test_create_report(self):
        """Test user can report an article"""
        self.client.post(self.url, self.comment_data,
                         format='json')
        response = self.client.post(
            self.report_url, self.report_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
