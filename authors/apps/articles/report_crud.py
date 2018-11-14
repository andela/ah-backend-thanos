from rest_framework.response import Response
from rest_framework import status
from authors.apps.authentication.send_email_util import SendEmail


def report_article(self, request, article_id):
    report = {'user': request.user.id,
              'article': article_id,
              'reason': request.data.get('reason')}
    serializer = self.serializer_class(data=report)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    reason = report['reason']
    user = request.user.email
    self.email = 'donotreply.websitemailer@gmail.com'
    self.mail_subject = "This article has been Reported!"
    self.message = """
    Hi Admin,
    This article has been reported by {}:
    {}://{}/api/articles/{}

    Reason: {}
    """.format(user, request.scheme, request.get_host(), article_id, reason)
    SendEmail.send_email(self, self.mail_subject, self.message, self.email)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
