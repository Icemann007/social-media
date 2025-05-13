from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from social.models import Profile, Post, Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "username",
            "password",
            "is_staff",
            "gender",
        ]
        read_only_fields = ["id", "is_staff"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
                "label": _("Password"),
            }
        }

    def create(self, validated_data):
        """Create User with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update User with encrypted password"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "bio",
            "profile_picture",
            "created_at",
            "updated_at",
        ]


class ProfileMeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    username = serializers.CharField(source="user.username")
    gender = serializers.ChoiceField(
        choices=get_user_model().GenderChoices, source="user.gender"
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "username",
            "gender",
            "bio",
            "profile_picture",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        user_instance = instance.user
        for attr, value in user_data.items():
            if attr in ("email", "first_name", "last_name", "username", "gender"):
                setattr(user_instance, attr, value)
            user_instance.save()
        return instance


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "content",
            "image",
            "created_at",
            "updated_at",
        ]


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "image",
            "created_at",
            "updated_at",
        ]


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = [
            "id",
            "follower",
            "following",
            "created_at",
        ]

    def validate(self, data):
        if data["follower"] == data["following"]:
            raise serializers.ValidationError("You cannot follow yourself.")
        return data
