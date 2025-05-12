from rest_framework import generics, viewsets

from social.models import Post, Profile, Follow
from social.serializers import (
    UserSerializer,
    PostSerializer,
    ProfileSerializer,
    FollowSerializer,
    ProfileListSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ProfileViewSets(viewsets.ModelViewSet):
    queryset = Profile.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        return ProfileSerializer


class PostViewSets(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class FollowViewSets(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
