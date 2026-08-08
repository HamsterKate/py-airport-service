from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

from user.serializers import (
    UserMeSerializer,
    UserSerializer,
)


@extend_schema(
    summary="Register a new user",
    description=(
        "Create a new customer account. "
        "New users are always registered with the Customer role."
    ),
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


@extend_schema(
    summary="Retrieve or update current user",
    description=(
        "Retrieve or update the profile "
        "of the authenticated user."
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user