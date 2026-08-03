from rest_framework.permissions import SAFE_METHODS, BasePermission

from user.models import User


class IsDispatcherOrReadOnly(BasePermission):
    """
    Everyone can read.
    Only dispatchers can modify data.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.role == User.Roles.DISPATCHER
            )
        )


class IsCrewOrDispatcher(BasePermission):
    """
    Access for crew members and dispatchers.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.role in (
                    User.Roles.CREW,
                    User.Roles.DISPATCHER,
                )
            )
        )


class IsDispatcher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.role == User.Roles.DISPATCHER
            )
        )
