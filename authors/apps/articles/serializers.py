from rest_framework import serializers
from .models import Article, Comment, Thread

from .validators import Validator

from ..core.utils.generate_author_details import to_represent_article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

    def to_representation(self, data):
        '''
        Show author's actual details instead of author's id
        '''
        article_details = super().to_representation(data)
        return to_represent_article(article_details)

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


class ArticlesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['slug', 'title', 'description', 'body',
                  'tag_list', 'image_url', 'audio_url']


class CommentSerializer(serializers.ModelSerializer):

    def to_representation(self, data):

        comment_details = super().to_representation(data)

        return to_represent_article(comment_details)

    def validate(self, data):
        validator = Validator
        comment_body = data.get("comment_body", None)

        validator.starts_with_letter("comment_body", comment_body)
        return data

    def create(self, validated_data):
        author = self.context.get('author', None)
        article = self.context.get('article', None)
        comment = Comment.objects.create(
            author=author,
            article=article,
            **validated_data
        )
        return comment

    class Meta:
        model = Comment
        fields = ('id', 'comment_body', 'author',
                  'created_at', 'updated_at')

        read_only_fields = ('author',)


class ThreadCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        author = self.context.get('author', None)
        comment = self.context.get('comment', None)
        thread = Thread.objects.create(
            author=author,
            comment=comment,
            **validated_data
        )
        return thread

    class Meta:
        model = Thread
        fields = ('id', 'thread_body', 'author', 'comment',
                  'created_at', 'updated_at')

        read_only_fields = ('author', 'comment')
