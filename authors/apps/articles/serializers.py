from rest_framework import serializers
from .models import (Article, Comment, Thread, LikeArticle, LikeComment,
                     Rating,
                     FavoriteArticle, Bookmark, ReportArticle,)

from rest_framework.exceptions import NotFound


from authors.apps.authentication.models import User
from authors.apps.core.custom_validators import ValidateUserData
from django.db.models import Avg

from ..core.utils.generate_author_details import to_represent_article

from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from taggit.models import Tag


class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    tag_list = TagListSerializerField()

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
            rating = Rating.objects.filter(article=article_details["id"])\
                                   .aggregate(Avg('rating'))
            favorites = FavoriteArticle.objects\
                                       .filter(article=article_details["id"])\
                                       .filter(favorite_status='True').count()
            article_details["likes"] = likes
            article_details["dislikes"] = dislikes
            article_details["Favorites_count"] = favorites
            article_details["rating"] = rating['rating__avg']
            if self.context.get('user_id') != user_details.id:
                del article_details["views_count"]
            if article_details["rating"] is not None:
                article_details["rating"] = round(rating['rating__avg'], 1)
            else:
                article_details["rating"] = 0

            return article_details
        raise NotFound(detail="User does not exist", code=404)

    def validate(self, data):
        validator = ValidateUserData()
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


class ArticlesUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    tag_list = TagListSerializerField()

    class Meta:
        model = Article
        fields = ['slug', 'title', 'description', 'body',
                  'tag_list', 'image_url', 'audio_url']


class ArticlesUpdatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ['views_count']


class CommentSerializer(serializers.ModelSerializer):

    def to_representation(self, data):

        comment_details = super().to_representation(data)
        likes = LikeComment.objects.filter(comment=comment_details["id"])\
            .filter(like_status='like').count()
        dislikes = LikeComment.objects\
            .filter(comment=comment_details["id"])\
            .filter(like_status='dislike').count()
        comment_details["likes"] = likes
        comment_details["dislikes"] = dislikes

        return to_represent_article(comment_details, user='comment_author')

    def validate(self, data):
        validator = ValidateUserData()
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

    def to_representation(self, data):

        thread_details = super().to_representation(data)

        return to_represent_article(thread_details, user='thread_author')

    def create(self, validated_data):
        author = self.context.get('thread_author', None)
        comment = self.context.get('comment', None)
        thread = Thread.objects.create(
            thread_author=author,
            comment=comment,
            **validated_data
        )
        return thread

    def validate(self, data):
        validator = ValidateUserData()
        thread_body = data.get("thread_body", None)
        validator.starts_with_letter("thread_body", thread_body)
        return data

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
        like_status_details = super().to_representation(data)

        return to_represent_article(like_status_details, user='user')


class LikeCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikeComment
        fields = '__all__'

    def to_representation(self, data):
        '''
        Show author's actual details instead of author's id
        '''
        like_status_details = super(
            LikeCommentSerializer, self).to_representation(data)
        if User.objects.filter(pk=int(like_status_details["user"])).exists():
            user_details = User.objects.get(
                pk=int(like_status_details["user"]))
            like_status_details["user"] = user_details.username
            return like_status_details
        raise NotFound(detail="User does not exist", code=404)


class FavoriteStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteArticle
        fields = '__all__'

    def to_representation(self, data):
        '''
        Show author's actual details instead of author's id
        '''
        favorite_details = super(
            FavoriteStatusSerializer, self).to_representation(data)
        if User.objects.filter(pk=int(favorite_details["user"])).exists():
            user_details = User.objects.get(
                pk=int(favorite_details["user"]))
            favorite_details["user"] = user_details.username
            return favorite_details
        raise NotFound(detail="User does not exist", code=404)


class GetFavoriteArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteArticle
        fields = '__all__'

    def to_representation(self, data):
        '''
        Show author's actual details instead of author's id
        '''
        favorite_details = super(
            GetFavoriteArticleSerializer, self).to_representation(data)
        article = Article.objects.get(pk=int(favorite_details["article"]))
        return ArticleSerializer(article).data


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
        read_only_fields = ('bookmarked_at',)


class FavoriteStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteArticle
        fields = ['favorite_status']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ReportArticleSerializer(serializers.ModelSerializer):
    reported_by = serializers.ReadOnlyField(source='user.email')
    article_author = serializers.ReadOnlyField(source='article.author.email')

    class Meta:
        model = ReportArticle
        fields = ['reason', 'article', 'user', 'reported_by',
                  'article_author', 'reported_at']
