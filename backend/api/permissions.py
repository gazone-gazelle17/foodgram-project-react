from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):

    def __init__(self, field_name='author'):
        self.field_name = field_name

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return getattr(obj, self.field_name) == request.user
