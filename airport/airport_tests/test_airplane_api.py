from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from airport.models import Airplane
from airport.airport_tests.helpers import (
    create_airplane,
    create_airplane_type,
)
from user.user_tests.helpers import (
    create_dispatcher,
    create_user,
)


AIRPLANE_URL = reverse("airport:airplane-list")


def detail_url(airplane_id: int) -> str:
    return reverse(
        "airport:airplane-detail",
        args=[airplane_id],
    )


class PublicAirplaneApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_list_airplanes(self):
        create_airplane(name="Boeing 737")
        create_airplane(name="Airbus A320")

        res = self.client.get(AIRPLANE_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(res.data), 2)


    def test_retrieve_airplane(self):
        airplane = create_airplane()

        res = self.client.get(
            detail_url(airplane.id)
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            res.data["id"],
            airplane.id,
        )


    def test_create_requires_authentication(self):
        payload = {
            "name": "New Plane",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": create_airplane_type().id,
            "registration_number": "UR-NEW",
        }

        res = self.client.post(
            AIRPLANE_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class PrivateAirplaneApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)


    def test_customer_cannot_create_airplane(self):
        payload = {
            "name": "New Plane",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": create_airplane_type().id,
            "registration_number": "UR-NEW",
        }

        res = self.client.post(
            AIRPLANE_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
        )


    def test_customer_can_list_airplanes(self):
        create_airplane()

        res = self.client.get(
            AIRPLANE_URL
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )


class DispatcherAirplaneApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.dispatcher = create_dispatcher()
        self.client.force_authenticate(
            self.dispatcher
        )

    def test_dispatcher_can_create_airplane(self):
        payload = {
            "name": "Boeing 777",
            "rows": 50,
            "seats_in_row": 8,
            "airplane_type": create_airplane_type().id,
            "registration_number": "UR-B777",
        }

        res = self.client.post(
            AIRPLANE_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Airplane.objects.filter(
                registration_number="UR-B777"
            ).exists()
        )

    def test_registration_number_must_be_unique(self):
        create_airplane(
            registration_number="UR-123"
        )

        payload = {
            "name": "Another plane",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": create_airplane_type().id,
            "registration_number": "UR-123",
        }

        res = self.client.post(
            AIRPLANE_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_filter_by_airplane_type(self):
        first_type = create_airplane_type(
            name="Boeing"
        )
        second_type = create_airplane_type(
            name="Airbus"
        )

        create_airplane(
            airplane_type=first_type
        )
        create_airplane(
            airplane_type=second_type,
            registration_number="UR-456",
        )

        res = self.client.get(
            AIRPLANE_URL,
            {
                "airplane_type": first_type.id
            },
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(res.data),
            1,
        )

    def test_airplanes_are_ordered_by_name(self):
        create_airplane(name="Zulu")
        create_airplane(
            name="Alpha",
            registration_number="UR-999",
        )

        res = self.client.get(
            AIRPLANE_URL
        )

        self.assertEqual(
            res.data[0]["name"],
            "Alpha",
        )
