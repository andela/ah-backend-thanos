from authors.apps.profiles.models import Follow
from authors.apps.authentication.models import User
from authors.apps.authentication.send_email_util import SendEmail
from authors.apps.articles.models import (Comment, FavoriteArticle)
from celery import shared_task


@shared_task
def notification(user):
    followers = Follow.objects.filter(followee=user)  # pragma: no cover
    for follows in followers:  # pragma: no cover
        follower_id = follows.follower.id  # pragma: no cover
        if User.objects.filter(id=follower_id, is_subscribed=False):  # pragma: no cover
            return None  # pragma: no cover
        else:  # pragma: no cover
            follower_email = follows.follower.email  # pragma: no cover
            send_email = SendEmail()  # pragma: no cover
            mail_subject = "Update"  # pragma: no cover
            message = """ 
                An author you follow just posted an article
                """  # pragma: no cover
            send_email.send_email(mail_subject, message,
                                  follower_email)  # pragma: no cover


@shared_task
def notification_new_comment(user, article_id):
    favorite_ids = FavoriteArticle.objects.filter(user=user,  # pragma: no cover
                                                  article=article_id)
    for favorite_id in favorite_ids:  # pragma: no cover
        article = favorite_id.article  # pragma: no cover
        user = favorite_id.user  # pragma: no cover
        user_email = User.objects.get(id=user.id).email  # pragma: no cover
        if article.id == article_id:  # pragma: no cover
            send_email = SendEmail()  # pragma: no cover
            mail_subject = "Update"  # pragma: no cover
            message = """ 
                An article you favorited has a new comment.
                """  # pragma: no cover
            send_email.send_email(mail_subject, message,
                                  user_email)  # pragma: no cover
