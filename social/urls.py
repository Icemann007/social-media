from django.urls import path, include
from rest_framework import routers

from social.views import (
    ProfileViewSets,
    PostViewSets,
    FollowViewSets,
    CreateUserView,
    LoginUserView, LogoutUserView,
)

app_name = "social"

router = routers.DefaultRouter()

router.register("profiles", ProfileViewSets)
router.register("posts", PostViewSets)
router.register("follows", FollowViewSets)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", LoginUserView.as_view(), name="get_token"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
]
