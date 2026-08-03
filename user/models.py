from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

from user.managers import UserManager


class User(AbstractUser):
    class Roles(models.TextChoices):
        DISPATCHER = "dispatcher", _("Dispatcher")
        CREW = "crew", _("Crew")
        CUSTOMER = "customer", _("Customer")

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CUSTOMER,
    )
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
