import os
import tempfile

from PIL import Image
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from airport.models import AirplaneType
from airport.airport_tests.helpers import create_airplane_type
from user.user_tests.helpers import create_dispatcher, create_user

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")


def detail_url(airplane_type_id: int) -> str:
    return reverse(
        "airport:airplanetype-detail",
        args=[airplane_type_id],
    )


def upload_url(airplane_type_id: int) -> str:
    return reverse(
        "airport:airplanetype-upload-image",
        args=[airplane_type_id],
    )


class PublicAirplaneTypeApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_airplane_types(self):
        create_airplane_type(name="Boeing 737")
        create_airplane_type(name="Airbus A320")

        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_airplane_type(self):
        airplane_type = create_airplane_type()

        res = self.client.get(detail_url(airplane_type.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], airplane_type.id)

    def test_create_requires_authentication(self):
        payload = {"name": "ATR-72"}

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAirplaneTypeApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_customer_cannot_create_airplane_type(self):
        payload = {"name": "ATR-72"}

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_can_list_airplane_types(self):
        create_airplane_type()

        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class DispatcherAirplaneTypeApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.dispatcher = create_dispatcher()
        self.client.force_authenticate(self.dispatcher)

    def test_dispatcher_can_create_airplane_type(self):
        payload = {
            "name": "ATR-72",
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            AirplaneType.objects.filter(
                name=payload["name"]
            ).exists()
        )

    def test_create_duplicate_name_fails(self):
        create_airplane_type(name="ATR-72")

        payload = {
            "name": "ATR-72",
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_airplane_types_are_ordered_by_name(self):
        create_airplane_type(name="Zulu")
        create_airplane_type(name="Alpha")

        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(
            res.data[0]["name"],
            "Alpha",
        )

    def upload_url(airplane_type_id: int):
        return reverse(
            "airport:airplanetype-upload-image",
            args=[airplane_type_id],
        )


class AirplaneTypeImageUploadTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.dispatcher = create_dispatcher()
        self.client.force_authenticate(self.dispatcher)

        self.airplane_type = create_airplane_type()

    def test_upload_image(self):
        url = upload_url(self.airplane_type.id)

        with tempfile.NamedTemporaryFile(suffix=".png") as image_file:
            img = Image.new("RGB", (20, 20))
            img.save(image_file, format="PNG")
            image_file.seek(0)

            res = self.client.post(
                url,
                {"image": image_file},
                format="multipart",
            )

        self.airplane_type.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane_type.image.path))

    def tearDown(self):
        self.airplane_type.image.delete()

    def test_upload_invalid_image(self):
        url = upload_url(self.airplane_type.id)

        res = self.client.post(
            url,
            {"image": "not image"},
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
