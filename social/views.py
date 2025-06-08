from django.db import IntegrityError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, mixins, status, viewsets
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


class ProfileViewSet(
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter by user username (ex. &username=user)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of users profiles."""
        return super().list(request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    owner_attr = "author"
    permission_classes = [IsOwnerAttributeOrReadOnly]

    def _filter_by_hashtag(self, queryset):
        hashtag = self.request.query_params.get("hashtag")
        if hashtag:
            queryset = queryset.filter(hashtags__icontains=hashtag)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        description="Return posts created by the currently authenticated user.",
        parameters=[
            OpenApiParameter(
                "hashtag",
                type=OpenApiTypes.STR,
                description="Filter by post hashtag (ex. &hashtag=hashtag)",
            ),
        ],
    )
    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        user = self.request.user
        posts = Post.objects.filter(author__username=user)
        posts = self._filter_by_hashtag(posts)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Return posts from users that the current user is following.",
        parameters=[
            OpenApiParameter(
                "hashtag",
                type=OpenApiTypes.STR,
                description="Filter by post hashtag (ex. &hashtag=hashtag)",
            ),
        ],
    )
    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def following(self, request):
        following_users = Follow.objects.filter(follower=request.user).values_list(
            "following", flat=True
        )
        posts = Post.objects.filter(author__in=following_users)
        posts = self._filter_by_hashtag(posts)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_permissions(self):
        if self.action in ["retrieve", "destroy"]:
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        try:
            serializer.save(follower=self.request.user)
        except IntegrityError:
            raise ValidationError("You already follow this user.")

    @extend_schema(description="Return a list of users who follow the current user.")
    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def followers(self, request):
        user = request.user
        queryset = Follow.objects.filter(following=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description="Return a list of users the current user is following.")
    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def following(self, request):
        user = request.user
        queryset = Follow.objects.filter(follower=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
