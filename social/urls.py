from django.urls import path, include
from rest_framework import routers

from social.views import ProfileViewSets, PostViewSets, FollowViewSets, CreateUserView

app_name = "social"

router = routers.DefaultRouter()

router.register("profiles", ProfileViewSets)
router.register("posts", PostViewSets)
router.register("follows", FollowViewSets)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", CreateUserView.as_view(), name="create"),
]
