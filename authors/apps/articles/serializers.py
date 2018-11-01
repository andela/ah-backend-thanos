import re
from rest_framework import serializers
from rest_framework.exceptions import APIException
from .models import Article
from authors.apps.authentication.models import User
from .validators import Validator


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

    def to_representation(self, data):
        '''
        Show author's actual details instead of author's id
        '''
        article_details = super(ArticleSerializer, self).to_representation(data)
        if User.objects.filter(pk=int(article_details["author"])).exists():
            user_details = User.objects.get(pk=int(article_details["author"]))
            article_details["author"] = {
                "id": user_details.id,
                "username": user_details.username,
                "email": user_details.email}
            return article_details
        raise APIException({"error": "User does not exist"})

    def validate(self, data):
        validator = Validator
        title = data.get("title", None)
        description = data.get("description", None)
        body = data.get("body", None)
        tag_list = data.get("tag_list", None)

        validator.starts_with_letter("title", title)
        validator.starts_with_letter("description", description)
        validator.starts_with_letter("body", body)
        for tag in tag_list:
            validator.starts_with_letter("tag", tag)
        return data
