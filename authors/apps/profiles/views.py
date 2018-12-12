from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


from .models import Profile, Follow
from .serializers import (
    ProfileSerializer,
    FollowerFolloweePairSerializer,
    FollowSerializer,
)
from .renderers import ProfileJSONRenderer
from .exceptions import UserCannotEditProfile

from authors.apps.core.utils.user_management import (
    get_id_from_token,
    getUserFromDatabase,
    getProfileFromDatabase,
    validateCurrentUserSelectedUser
)


class ProfileRetrieveUpdateAPIView(GenericAPIView):
    """
    get: Allow users  to retrieve their profiles
    put: Allow users  to edit their profiles
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def get(self, request, username, *args, **kwargs):
        user = getUserFromDatabase(username=username)
        serializer = self.serializer_class(user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, username, *args, **kwargs):
        serializer_data = request.data.get('profiles', {})
        user = getUserFromDatabase(username=username)
        try:
            user_id, username, = get_id_from_token(request)
            if user.username != username:
                raise UserCannotEditProfile
        except Exception:
            raise UserCannotEditProfile

        serializer_data = {
            'first_name':
            serializer_data.get('first_name',
                                request.user.profile.last_name),
            'last_name':
            serializer_data.get('last_name',
                                request.user.profile.last_name),
            'bio': serializer_data.get('bio', request.user.profile.bio),
            'image': serializer_data.get('image', request.user.profile.image)
        }

        serializer = self.serializer_class(
            request.user.profile,
            data=serializer_data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user.profile, serializer_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileListAPIView(ListAPIView):
    """Allow user to view other user profiles"""
    renderer_classes = (ProfileJSONRenderer,)
    permission_classes = (IsAuthenticated, )
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class FollowGenericAPIView(GenericAPIView):
    """
    post: Follow another user
    delete: Unfollow a user
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)

    def post(self, request, username, *args, **kwargs):
        user_to_follow = getUserFromDatabase(username=username)
        current_user_id, current_username = get_id_from_token(request)
        validateCurrentUserSelectedUser(current_user_id, user_to_follow.id)
        follow_data = {
            "follower": current_user_id,
            "followee": user_to_follow.id
        }
        serializer = FollowerFolloweePairSerializer(data=follow_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # return profile of the user you just followed
        profile_followed = getProfileFromDatabase(user_id=user_to_follow.id)
        user_serializer = ProfileSerializer(profile_followed)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, username, *args, **kwargs):
        user_to_unfollow = getUserFromDatabase(username=username)  # validate
        id = user_to_unfollow.id
        current_id, current_username = get_id_from_token(request)
        if Follow.objects.filter(follower=current_id, followee=id).exists():
            Follow.objects.get(follower=current_id, followee=id).delete()
            return Response({"message": "You have Unfollowed the User"},
                            status=status.HTTP_200_OK)
        raise NotFound(detail="You are currently not following this user")


class FollowingListAPIView(ListAPIView):
    """
    get: Get all the user's one is following
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, username, *args, **kwargs):
        user = getUserFromDatabase(username=username)  # validate user exists
        follow = Follow.objects.filter(follower=user.id)
        if follow.count() == 0:
            raise NotFound(detail="This user is not following anyone")
        serializer = FollowSerializer(
            follow, many=True,
            context={'user_type': 'followee'}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersListAPIView(ListAPIView):
    """
    get: Get all followers of a user
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, username, *args, **kwargs):
        user = getUserFromDatabase(username=username)  # validate user exists
        follow = Follow.objects.filter(followee=user.id)
        if follow.count() == 0:
            raise NotFound(detail="This user is not being followed by anyone")
        serializer = FollowSerializer(follow, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
