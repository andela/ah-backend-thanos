from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from ...settings import DEFAULT_FROM_EMAIL, SEND_GRID_API_KEY, TESTING

import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail

User = get_user_model()


class SendEmail():

    def send_email(self, mail_subject, message, email):
        if TESTING is True:
            send_mail(mail_subject, message, DEFAULT_FROM_EMAIL,
                      [email], fail_silently=False)
        elif TESTING is False:  # pragma: no cover
            sg = sendgrid.SendGridAPIClient(
                apikey=SEND_GRID_API_KEY)  # pragma: no cover
            from_email = Email("noreply@authourshaven.com")  # pragma: no cover
            to_email = Email(email)  # pragma: no cover
            subject = mail_subject  # pragma: no cover
            content = Content("text/plain", message)  # pragma: no cover
            mail = Mail(from_email, subject, to_email,
                        content)  # pragma: no cover
            response = sg.client.mail.send.post(
                request_body=mail.get())  # pragma: no cover
            print(response.status_code)  # pragma: no cover
            print(response.body)  # pragma: no cover
            print(response.headers)  # pragma: no cover
