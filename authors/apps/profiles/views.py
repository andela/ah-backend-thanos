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
    Allow users  to retrieve and edit their profiles Params: username:
    A username is needed in order to get a specific profile.
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
    permission_classes = (IsAuthenticated, )
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class FollowGenericAPIView(GenericAPIView):
    """
    POST follow
    DELETE unfollow
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)

    def post(self, request, pk, *args, **kwargs):
        user_to_follow = getUserFromDatabase(pk)
        current_user_id, email = get_id_from_token(request)
        validateCurrentUserSelectedUser(current_user_id, user_to_follow.id)
        follow_data = {"follower": current_user_id, "followee": pk}
        serializer = FollowerFolloweePairSerializer(data=follow_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # return profile of the user you just followed
        profile_followed = getProfileFromDatabase(user_id=pk)
        user_serializer = ProfileSerializer(profile_followed)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk, *args, **kwargs):
        getUserFromDatabase(pk)  # validate user exists
        current_id, email = get_id_from_token(request)
        if Follow.objects.filter(follower=current_id, followee=pk).exists():
            Follow.objects.get(follower=current_id, followee=pk).delete()
            return Response({"message": "You have Unfollowed the User"},
                            status=status.HTTP_200_OK)
        raise NotFound(detail="You are currently not following this user")


class FollowingListAPIView(ListAPIView):
    """GET all user's one is following"""
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, pk, *args, **kwargs):
        getUserFromDatabase(pk)  # validate user exists
        follow = Follow.objects.filter(follower=pk)
        if follow.count() == 0:
            raise NotFound(detail="This user is not following anyone")
        serializer = FollowSerializer(
            follow, many=True,
            context={'user_type': 'followee'}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersListAPIView(ListAPIView):
    """GET all followers of a user"""
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, pk, *args, **kwargs):
        getUserFromDatabase(pk)  # validate user exists
        follow = Follow.objects.filter(followee=pk)
        if follow.count() == 0:
            raise NotFound(detail="This user is not being followed by anyone")
        serializer = FollowSerializer(follow, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
