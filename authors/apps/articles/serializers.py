from rest_framework import serializers
from .models import Article, Comment, Thread, LikeArticle, Rating, Bookmark

from rest_framework.exceptions import NotFound


from authors.apps.authentication.models import User
from .validators import Validator
from django.db.models import Avg

from ..core.utils.generate_author_details import to_represent_article


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'

    def to_representation(self, data):
        '''
        Show author's actual details instead of author's id
        '''
        article_details = super(
            ArticleSerializer, self).to_representation(data)
        if User.objects.filter(pk=int(article_details["author"])).exists():
            user_details = User.objects.get(pk=int(article_details["author"]))
            article_details["author"] = {
                "id": user_details.id,
                "username": user_details.username,
                "email": user_details.email}
            likes = LikeArticle.objects.filter(article=article_details["id"])\
                                       .filter(like_status='like').count()
            dislikes = LikeArticle.objects\
                                  .filter(article=article_details["id"])\
                                  .filter(like_status='dislike').count()
            rating = Rating.objects.filter(
                article=article_details["id"]).aggregate(Avg('rating'))
            article_details["likes"] = likes
            article_details["dislikes"] = dislikes
            article_details["rating"] = rating['rating__avg']
            return article_details
        raise NotFound(detail="User does not exist", code=404)

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
        author = self.context.get('comment_author', None)
        article = self.context.get('article', None)
        comment = Comment.objects.create(
            comment_author=author,
            article=article,
            **validated_data
        )
        return comment

    class Meta:
        model = Comment
        fields = ('id', 'comment_body', 'comment_author',
                  'created_at', 'updated_at')

        read_only_fields = ('comment_author',)


class ThreadCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        author = self.context.get('thread_author', None)
        comment = self.context.get('comment', None)
        thread = Thread.objects.create(
            thread_author=author,
            comment=comment,
            **validated_data
        )
        return thread

    class Meta:
        model = Thread
        fields = ('id', 'thread_body', 'thread_author',
                  'created_at', 'updated_at')

        read_only_fields = ('thread_author',)


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikeArticle
        fields = '__all__'

    def to_representation(self, data):
        '''
        Show author's actual details instead of author's id
        '''
        like_status_details = super(
            LikeSerializer, self).to_representation(data)
        if User.objects.filter(pk=int(like_status_details["user"])).exists():
            user_details = User.objects.get(
                pk=int(like_status_details["user"]))
            like_status_details["user"] = user_details.username
            return like_status_details
        raise NotFound(detail="User does not exist", code=404)


class LikeStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikeArticle
        fields = ['like_status']


class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ['rating', 'reader', 'article']

    def to_representation(self, data):

        article_slug = {}
        article_rating = super(RatingSerializer, self).to_representation(data)

        if User.objects.filter(pk=int(article_rating['reader'])).exists():
            user_detail = User.objects.get(pk=int(article_rating["reader"]))

        if Rating.objects.filter(pk=int(article_rating['article'])).exists():
            article_slug = Article.objects.get(
                pk=int(article_rating['article']))

            article_rating["reader"] = {
                "username": user_detail.username,
                "article_slug": article_slug.slug

            }

        return article_rating


class BookmarkSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='article.author.username')
    article = serializers.ReadOnlyField(source='article.id')
    article_title = serializers.ReadOnlyField(source='article.title')

    class Meta:
        model = Bookmark
        fields = ['author', 'article', 'article_title', 'bookmarked_at']
