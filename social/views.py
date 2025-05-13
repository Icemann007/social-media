from rest_framework import generics, viewsets, status, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from social.models import Post, Profile, Follow
from social.serializers import (
    UserSerializer,
    PostSerializer,
    ProfileSerializer,
    FollowSerializer,
    AuthTokenSerializer,
    ProfileMeSerializer,
    PostListSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"detail": "Logged out successfully."})


class ProfileViewSets(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Profile.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        username = self.request.query_params.get("username")

        if username:
            queryset = queryset.filter(user__username__icontains=username)

        return queryset

    @action(
        detail=False,
        methods=["GET", "PUT", "PATCH", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        profile = request.user.profile
        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PUT":
            serializer = self.get_serializer(profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PATCH":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "DELETE":
            user = request.user
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == "me":
            return ProfileMeSerializer
        return ProfileSerializer


class PostViewSets(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FollowViewSets(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
