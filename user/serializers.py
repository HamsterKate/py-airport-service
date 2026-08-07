from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password"
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
            }
        }

    def create(
        self,
        validated_data: dict
    ) -> User:
        """Create a user with a hashed password."""
        return User.objects.create_user(**validated_data)


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
        )
        read_only_fields = (
            "id",
            "role",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "required": False,
            },
        }

    def update(
        self,
        instance: User,
        validated_data: dict,
    ) -> User:
        """Update a user and hash the password if provided."""
        password = validated_data.pop("password", None)

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
