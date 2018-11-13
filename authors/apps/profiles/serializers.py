from rest_framework import serializers

from authors.apps.core.utils.user_management import (
    getUserFromDatabase, getProfileFromDatabase
)
from .models import Profile, Follow
from.validators import is_profile_valid


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for creating a profile"""
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False,
                                min_length=5,
                                max_length=255)
    first_name = serializers.CharField(allow_blank=True, required=False,
                                       min_length=2, max_length=50)
    last_name = serializers.CharField(allow_blank=True, required=False,
                                      min_length=2,
                                      max_length=50)

    def validate(self, data):
        bio = data.get('bio', None)
        first_name = data.get('first_name', None)
        last_name = data.get("last_name", None)

        is_profile_valid(self, bio, first_name, last_name)
        return {'bio': bio, 'first_name': first_name, 'last_name': last_name}

    class Meta:
        model = Profile
        fields = ['username', 'bio', 'image', 'first_name',
                  'last_name', 'created_at', 'updated_at']


class FollowerFolloweePairSerializer(serializers.ModelSerializer):
    """
    Used to post pairs of Followers and their matching Followees
    into the Follow Model
    """
    def validate(self, data):
        follower = data.get('follower')
        followee = data.get('followee')
        if Follow.objects.filter(follower=follower,
                                 followee=followee).exists():
            raise serializers.ValidationError(
                detail="You are already following this user",
                code=400)
        return data

    class Meta:
        model = Follow
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    """Used to display followers and followees of a specific user"""
    def to_representation(self, data):
        follow_details = super(FollowSerializer,
                               self).to_representation(data)
        if self.context.get("user_type") == 'followee':
            profile = getProfileFromDatabase(
                user_id=follow_details['followee'])
        else:
            profile = getProfileFromDatabase(
                user_id=follow_details['follower'])
        return (ProfileSerializer(profile).data)

    class Meta:
        model = Follow
        fields = '__all__'
