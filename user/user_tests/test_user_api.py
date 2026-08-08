from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from user.user_tests.helpers import (
    create_dispatcher,
    create_user,
)


User = get_user_model()

REGISTER_URL = reverse("user:create")
ME_URL = reverse("user:manage")


class PublicUserApiTests(APITestCase):
    """Tests for unauthenticated user API."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self) -> None:
        payload = {
            "email": "user@example.com",
            "password": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(REGISTER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

        self.assertNotIn("password", response.data)
        self.assertEqual(user.role, User.Roles.CUSTOMER)

    def test_create_user_with_existing_email_fails(self) -> None:
        create_user(email="user@example.com")

        payload = {
            "email": "user@example.com",
            "password": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(REGISTER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_short_password_fails(self) -> None:
        payload = {
            "email": "user@example.com",
            "password": "123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(REGISTER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            User.objects.filter(email=payload["email"]).exists()
        )

    def test_create_user_with_invalid_password_fails(self) -> None:
        payload = {
            "email": "user@example.com",
            "password": "password",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.client.post(REGISTER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            User.objects.filter(email=payload["email"]).exists()
        )

    def test_login_required_for_me_endpoint(self) -> None:
        response = self.client.get(ME_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_user_requires_email(self) -> None:
        payload = {
            "email": "",
            "password": "testpass123",
        }

        response = self.client.post(REGISTER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_normalizes_email(self) -> None:
        payload = {
            "email": "User@Example.COM",
            "password": "testpass123",
        }

        self.client.post(REGISTER_URL, payload)

        user = User.objects.get(email="User@example.com")
        self.assertEqual(user.email, "User@example.com")


class PrivateUserApiTests(APITestCase):
    """Tests for authenticated user API."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile(self) -> None:
        """Authenticated user can retrieve own profile."""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(
            res.data["first_name"],
            self.user.first_name,
        )
        self.assertEqual(
            res.data["last_name"],
            self.user.last_name,
        )
        self.assertEqual(
            res.data["role"],
            self.user.role,
        )

    def test_partial_update_profile(self) -> None:
        """Authenticated user can update own profile."""

        payload = {
            "first_name": "Updated",
            "last_name": "User",
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.user.first_name,
            payload["first_name"],
        )
        self.assertEqual(
            self.user.last_name,
            payload["last_name"],
        )

    def test_update_password(self) -> None:
        """Authenticated user can change own password."""

        payload = {
            "password": "newstrongpassword123",
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(
            self.user.check_password(payload["password"])
        )

    def test_role_is_read_only(self) -> None:
        """User cannot change own role."""

        payload = {
            "role": User.Roles.DISPATCHER,
        }

        self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.role,
            User.Roles.CUSTOMER,
        )

    def test_put_updates_profile(self) -> None:
        """Authenticated user can fully update own profile."""

        payload = {
            "email": self.user.email,
            "first_name": "New",
            "last_name": "Name",
        }

        res = self.client.put(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.user.first_name,
            payload["first_name"],
        )
        self.assertEqual(
            self.user.last_name,
            payload["last_name"],
        )

    def test_post_not_allowed(self) -> None:
        """POST method is not allowed for profile endpoint."""

        res = self.client.post(ME_URL, {})

        self.assertEqual(
            res.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_password_too_short(self):
        """Password validation is applied."""

        payload = {
            "password": "123",
        }

        res = self.client.patch(ME_URL, payload)

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
