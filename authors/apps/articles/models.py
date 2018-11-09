
from django.db import models
from django.utils import timezone
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from django.contrib.postgres.fields import ArrayField


from ..core.models import TimeStampedModel


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, blank=False, unique=True)
    title = models.CharField(max_length=300, blank=False)
    description = models.TextField(blank=False)
    body = models.TextField(blank=False)
    tag_list = ArrayField(models.CharField(max_length=200), blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favorited = models.BooleanField(default=False)
    favorites_count = models.IntegerField(default=0)
    image_url = models.URLField(blank=False)
    audio_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-updated_at']


class Comment(TimeStampedModel):
    """Defines the descriptive data for the different comments created"""
    comment_body = models.TextField(blank=False)
    comment_author = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE)
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


class Rating(models.Model):

    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def __str__(self):
        return self.rating


class Bookmark(models.Model):
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, blank=False, on_delete=models.CASCADE)
    bookmarked_at = models.DateTimeField(auto_created=True,
                                         auto_now=False, default=timezone.now)
