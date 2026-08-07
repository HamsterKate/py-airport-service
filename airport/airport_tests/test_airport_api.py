from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from airport.models import Airport
from airport.airport_tests.helpers import create_airport
from user.user_tests.helpers import create_dispatcher, create_user


AIRPORT_URL = reverse("airport:airport-list")


def detail_url(airport_id: int) -> str:
    return reverse(
        "airport:airport-detail",
        args=[airport_id],
    )


class PublicAirportApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_airports(self):
        create_airport(name="Boryspil")
        create_airport(name="Heathrow")

        res = self.client.get(AIRPORT_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(res.data), 2)

    def test_retrieve_airport(self):
        airport = create_airport()

        res = self.client.get(detail_url(airport.id))

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            res.data["id"],
            airport.id,
        )

    def test_create_requires_authentication(self):
        payload = {
            "name": "JFK",
        }

        res = self.client.post(
            AIRPORT_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class PrivateAirportApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_customer_cannot_create_airport(self):
        payload = {
            "name": "JFK",
        }

        res = self.client.post(
            AIRPORT_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_customer_can_list_airports(self):
        create_airport()

        res = self.client.get(AIRPORT_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )


class DispatcherAirportApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.dispatcher = create_dispatcher()
        self.client.force_authenticate(self.dispatcher)

    def test_dispatcher_can_create_airport(self):
        payload = {
            "name": "JFK Airport",
            "city": create_airport().city.id,
            "closest_big_city": "New York",
        }

        res = self.client.post(
            AIRPORT_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Airport.objects.filter(
                name="JFK Airport",
            ).exists()
        )

    def test_airports_are_ordered_by_name(self):
        create_airport(name="Zulu Airport")
        create_airport(name="Alpha Airport")

        res = self.client.get(AIRPORT_URL)

        self.assertEqual(
            res.data[0]["name"],
            "Alpha Airport",
        )
















