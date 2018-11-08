from rest_framework.exceptions import NotFound
from authors.apps.authentication.models import User


def to_represent_article(article_details):
    '''
    Show author's actual details instead of author's id
    '''
    if User.objects.filter(pk=int(article_details["author"])).exists():
        user_details = User.objects.get(pk=int(article_details["author"]))
        article_details["author"] = {
            "id": user_details.id,
            "username": user_details.username,
            "email": user_details.email}
        return article_details
    raise NotFound(detail="User does not exist")
