from rest_framework.permissions import SAFE_METHODS, BasePermission

from user.models import User


class IsDispatcher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.role == User.Roles.DISPATCHER
            )
        )


class IsDispatcherOrReadOnly(IsDispatcher):
    """
    Everyone can read.
    Only dispatchers can modify data.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            super().has_permission(request, view)
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





class IsCustomerOrDispatcher(BasePermission):
    """
    Access for customers and dispatchers.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.role in (
                    User.Roles.CUSTOMER,
                    User.Roles.DISPATCHER,
                )
            )
        )
