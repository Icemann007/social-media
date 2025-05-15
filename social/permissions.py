from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerAttributeOrReadOnly(BasePermission):
    owner_attr = "user"

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        owner_field = getattr(view, "owner_attr", self.owner_attr)
        return getattr(obj, owner_field) == request.user


class IsOwner(IsOwnerAttributeOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            raise PermissionDenied("Please log in to access this resource.")

        if obj.follower != request.user:
            raise PermissionDenied(
                "You do not have permission to access this follow relationship."
            )

        return True
