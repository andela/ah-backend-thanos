from django.db import models

from authors.apps.authentication.models import User
from authors.apps.core.models import TimeStampedModel


class Profile(TimeStampedModel):
    """Defines the  descriptive data for the different user profiles created"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)
    first_name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name="follow_user_a")
    followee = models.ForeignKey(User, on_delete=models.CASCADE)
