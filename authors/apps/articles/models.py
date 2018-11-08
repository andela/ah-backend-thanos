from django.db import models
from authors.apps.authentication.models import User
from django.contrib.postgres.fields import ArrayField


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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']
