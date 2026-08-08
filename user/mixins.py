from django.contrib.auth.password_validation import validate_password


class PasswordValidationMixin:
    """Validate password using Django password validators."""

    def validate_password(self, value: str) -> str:
        validate_password(value, user=getattr(self, "instance", None))
        return value
