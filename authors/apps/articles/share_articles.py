from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response


from authors.apps.authentication.send_email_util import SendEmail


class ShareEmailAPIView(generics.CreateAPIView):
    """This class is for sharing articles by email"""
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, article_id, *args, **kwargs):
        user = request.user.username
        self.email = request.user.email
        self.mail_subject = "This article has been shared with you"
        self.message = """
        Hi {},
        This article has been shared with you:
        {}://{}/api/articles/{}
        """.format(user, request.scheme,
                   request.get_host(), article_id,)
        SendEmail.send_email(self, self.mail_subject, self.message, self.email)
        return Response({'detail': "Article has been successfully shared"},
                        status=status.HTTP_200_OK)


class ShareFacebookAPIView(generics.CreateAPIView):
    """This class is for sharing articles by facebook"""
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, article_id, *args, **kwargs):
        base_url = "https://www.facebook.com/sharer/sharer.php?u="
        fb_link = (
            base_url + "{}://{}/api/articles/{}".format(request.scheme,
                                                        request.get_host(),
                                                        article_id,))
        return Response({'detail': "Article has been successfully shared",
                         "link": fb_link},
                        status=status.HTTP_200_OK)


class ShareTwitterAPIView(generics.CreateAPIView):
    """This class is for sharing articles by twitter"""
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, article_id, *args, **kwargs):
        base_url = "https://twitter.com/home?status="
        heroku_link = "{}://{}/api/articles/{}".format(
            request.scheme,
            request.get_host(), article_id,)
        url_link = base_url + heroku_link
        return Response({'detail': "Article has been successfully shared",
                         "link": url_link},
                        status=status.HTTP_200_OK)
