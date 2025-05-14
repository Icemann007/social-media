from django.db import IntegrityError
from rest_framework import generics, mixins, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from social.models import Post, Profile, Follow
from social.permissions import IsOwnerAttributeOrReadOnly, IsOwner
from social.serializers import (
    UserSerializer,
    PostSerializer,
    ProfileSerializer,
    FollowSerializer,
    AuthTokenSerializer,
    ProfileListSerializer,
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


class ProfileViewSets(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Profile.objects.all()
    permission_classes = [IsOwnerAttributeOrReadOnly]

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

    def perform_destroy(self, instance):
        user = instance.user
        user.delete()


class PostViewSets(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    owner_attr = "author"
    permission_classes = [IsOwnerAttributeOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        user = self.request.user
        posts = Post.objects.filter(author__username=user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def following(self, request):
        following_users = Follow.objects.filter(follower=request.user).values_list(
            "following", flat=True
        )
        posts = Post.objects.filter(author__in=following_users)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowViewSets(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsOwner]

    def perform_create(self, serializer):
        try:
            serializer.save(follower=self.request.user)
        except IntegrityError:
            raise ValidationError("You already follow this user.")

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def followers(self, request):
        user = request.user
        queryset = Follow.objects.filter(following=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def following(self, request):
        user = request.user
        queryset = Follow.objects.filter(follower=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
