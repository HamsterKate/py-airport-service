from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from airport.models import Flight
from airport.airport_tests.helpers import (
    create_airplane,
    create_crew,
    create_flight,
    create_route,
)
from user.user_tests.helpers import create_dispatcher, create_user


FLIGHT_URL = reverse("airport:flight-list")


def detail_url(flight_id: int) -> str:
    return reverse(
        "airport:flight-detail",
        args=[flight_id],
    )


class PublicFlightApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_flights(self):
        create_flight(flight_number="PS101")
        create_flight(flight_number="PS102")

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_list_flights_returns_expected_fields(self):
        flight = create_flight()

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        flight_data = res.data[0]

        self.assertEqual(flight_data["id"], flight.id)
        self.assertEqual(
            flight_data["flight_number"],
            flight.flight_number,
        )
        self.assertIn("route", flight_data)
        self.assertIn("airplane", flight_data)
        self.assertIn("departure_time", flight_data)
        self.assertIn("arrival_time", flight_data)
        self.assertIn("duration", flight_data)
        self.assertIn("status", flight_data)
        self.assertIn("terminal", flight_data)
        self.assertIn("gate", flight_data)

    def test_retrieve_flight(self):
        flight = create_flight()

        res = self.client.get(detail_url(flight.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], flight.id)
        self.assertEqual(
            res.data["flight_number"],
            flight.flight_number,
        )

    def test_public_retrieve_does_not_include_crew(self):
        flight = create_flight()

        res = self.client.get(detail_url(flight.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn("crew", res.data)

    def test_list_flights_are_ordered_by_departure_time(self):
        from django.utils import timezone
        from datetime import timedelta

        departure = timezone.now()

        create_flight(
            flight_number="PS102",
            departure_time=departure + timedelta(hours=2),
        )
        create_flight(
            flight_number="PS101",
            departure_time=departure,
        )

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data[0]["flight_number"],
            "PS101",
        )


class PrivateFlightApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_customer_can_list_flights(self):
        create_flight()

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_customer_can_retrieve_flight(self):
        flight = create_flight()

        res = self.client.get(detail_url(flight.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], flight.id)

    def test_customer_cannot_create_flight(self):
        route = create_route()
        airplane = create_airplane()
        crew = [create_crew(), create_crew()]

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2030-01-01T10:00:00Z",
            "arrival_time": "2030-01-01T12:00:00Z",
            "flight_number": "PS999",
            "crew": [member.id for member in crew],
        }

        res = self.client.post(
            FLIGHT_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class DispatcherFlightApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.dispatcher = create_dispatcher()
        self.client.force_authenticate(self.dispatcher)

    def test_dispatcher_can_create_flight(self):
        route = create_route()
        airplane = create_airplane()
        crew = [create_crew(), create_crew()]

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2030-01-01T10:00:00Z",
            "arrival_time": "2030-01-01T12:00:00Z",
            "flight_number": "PS999",
            "crew": [member.id for member in crew],
        }

        res = self.client.post(
            FLIGHT_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        flight = Flight.objects.get(
            flight_number="PS999",
        )

        self.assertEqual(flight.route, route)
        self.assertEqual(flight.airplane, airplane)
        self.assertEqual(
            set(flight.crew.values_list("id", flat=True)),
            {member.id for member in crew},
        )

    def test_dispatcher_retrieve_contains_crew(self):
        flight = create_flight()

        res = self.client.get(detail_url(flight.id))

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("crew", res.data)
        self.assertEqual(
            len(res.data["crew"]),
            flight.crew.count(),
        )

    def test_dispatcher_retrieve_contains_full_airplane_data(self):
        flight = create_flight()

        res = self.client.get(detail_url(flight.id))

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        airplane = res.data["airplane"]

        self.assertIn("rows", airplane)
        self.assertIn("seats_in_row", airplane)
        self.assertIn("capacity", airplane)
        self.assertIn("airplane_type", airplane)

    def test_dispatcher_can_list_flights(self):
        create_flight()

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        # List endpoint intentionally uses FlightListSerializer,
        # so crew is not returned here.
        self.assertNotIn("crew", res.data[0])
