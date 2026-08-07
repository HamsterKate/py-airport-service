from __future__ import annotations

from user.models import User


def create_user(**params) -> User:
    """Create and return a user."""
    defaults = {
        "email": "user@example.com",
        "password": "Testpass123!",
        "first_name": "John",
        "last_name": "Doe",
    }
    defaults.update(params)

    return User.objects.create_user(**defaults)


def create_dispatcher(**params) -> User:
    """Create and return a dispatcher."""
    defaults = {
        "email": "dispatcher@example.com",
        "password": "Dispatcher123!",
        "first_name": "Jane",
        "last_name": "Smith",
        "role": User.Roles.DISPATCHER,
        "is_staff": True,
    }
    defaults.update(params)

    return User.objects.create_user(**defaults)
