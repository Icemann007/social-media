from rest_framework import generics, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from social.models import Post, Profile, Follow
from social.serializers import (
    UserSerializer,
    PostSerializer,
    ProfileSerializer,
    FollowSerializer,
    ProfileListSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"detail": "Logged out successfully."})


class ProfileViewSets(viewsets.ModelViewSet):
    queryset = Profile.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        username = self.request.query_params.get("username")

        if username:
            queryset = queryset.filter(user__username__icontains=username)

        return queryset

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
