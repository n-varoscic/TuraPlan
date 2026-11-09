from rest_framework.permissions import BasePermission

from .models import User


class IsDispatcher(BasePermission):
    """Dostop ima samo prijavljen disponent"""

    message = "Ni dostopa"

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.DISPATCHER


class IsDriver(BasePermission):
    """Dostop ima samo prijavljen voznik"""

    message = "Ni dostopa"

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.DRIVER
