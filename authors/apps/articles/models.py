from django.db import models
from django.utils import timezone
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from ..core.models import TimeStampedModel
from taggit.managers import TaggableManager


class Article(models.Model):
    author = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, blank=False, unique=True)
    title = models.CharField(max_length=300, blank=False)
    description = models.TextField(blank=False)
    body = models.TextField(blank=False)
    tag_list = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=False)
    audio_url = models.URLField(blank=True, null=True)
    views_count = models.IntegerField(default=0)
    read_time = models.IntegerField(default=0)

    class Meta:
        ordering = ['-updated_at']


class Comment(TimeStampedModel):
    """Defines the descriptive data for the different comments created"""
    comment_body = models.TextField(blank=False)
    comment_author = models.ForeignKey('profiles.Profile',
                                       on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class Thread (TimeStampedModel):
    """Defines the descriptive data for the different comments created"""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    thread_body = models.TextField(blank=False)
    thread_author = models.ForeignKey(Profile, on_delete=models.CASCADE)


class LikeArticle(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    LIKE_CHOICES = (
        (LIKE, 'like'),
        (DISLIKE, 'dislike'),)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    article_title = models.CharField(max_length=255)
    like_status = models.CharField(max_length=10,
                                   choices=LIKE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.like_status


class LikeComment(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    LIKE_CHOICES = (
        (LIKE, 'like'),
        (DISLIKE, 'dislike'),)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    comment_body = models.CharField(max_length=255)
    like_status = models.CharField(max_length=10,
                                   choices=LIKE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.like_status


class Rating(models.Model):

    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return self.rating


class Bookmark(models.Model):
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, blank=False, on_delete=models.CASCADE)
    bookmarked_at = models.DateTimeField(auto_created=True,
                                         auto_now=False, default=timezone.now)


class FavoriteArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    favorite_status = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.favorite_status


class ReportArticle(models.Model):
    reason = models.CharField(max_length=300, blank=False)
    article = models.ForeignKey(Article,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_created=True,
                                       auto_now=False, default=timezone.now)
