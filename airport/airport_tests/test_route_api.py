from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from airport.models import Route
from airport.airport_tests.helpers import create_airport, create_route
from user.user_tests.helpers import create_dispatcher, create_user


ROUTE_URL = reverse("airport:route-list")


def detail_url(route_id: int) -> str:
    return reverse(
        "airport:route-detail",
        args=[route_id],
    )


class PublicRouteApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_routes(self):
        create_route()
        create_route(
            source=create_airport(name="Lviv Airport"),
            destination=create_airport(
                name="Warsaw Airport",
            ),
        )

        res = self.client.get(ROUTE_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(res.data), 2)

    def test_retrieve_route(self):
        route = create_route()

        res = self.client.get(detail_url(route.id))

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            res.data["id"],
            route.id,
        )

    def test_create_requires_authentication(self):
        route = create_route()

        payload = {
            "source": route.source.id,
            "destination": route.destination.id,
            "distance": 500,
        }

        res = self.client.post(
            ROUTE_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class PrivateRouteApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_customer_cannot_create_route(self):
        route = create_route()

        payload = {
            "source": route.source.id,
            "destination": route.destination.id,
            "distance": 500,
        }

        res = self.client.post(
            ROUTE_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_customer_can_list_routes(self):
        create_route()

        res = self.client.get(ROUTE_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )


class DispatcherRouteApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.dispatcher = create_dispatcher()
        self.client.force_authenticate(self.dispatcher)

    def test_dispatcher_can_create_route(self):
        source = create_airport(
            name="Kyiv Airport",
        )
        destination = create_airport(
            name="Paris Airport",
        )

        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 2100,
        }

        res = self.client.post(
            ROUTE_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Route.objects.filter(
                source=source,
                destination=destination,
            ).exists()
        )

    def test_source_and_destination_must_be_different(self):
        airport = create_airport()

        payload = {
            "source": airport.id,
            "destination": airport.id,
            "distance": 100,
        }

        res = self.client.post(
            ROUTE_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_search_routes(self):
        kyiv = create_airport(name="Kyiv Airport")
        paris = create_airport(name="Paris Airport")
        london = create_airport(name="London Airport")

        create_route(
            source=kyiv,
            destination=paris,
        )
        create_route(
            source=kyiv,
            destination=london,
        )

        res = self.client.get(
            ROUTE_URL,
            {"search": "Paris"},
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(res.data), 1)
        self.assertEqual(
            res.data[0]["destination"],
            str(paris),
        )

    def test_routes_are_ordered_by_source_name(self):
        alpha = create_airport(name="Alpha Airport")
        zulu = create_airport(name="Zulu Airport")

        create_route(
            source=zulu,
            destination=create_airport(name="Paris Airport"),
        )
        create_route(
            source=alpha,
            destination=create_airport(name="London Airport"),
        )

        res = self.client.get(ROUTE_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            res.data[0]["source"],
            str(alpha),
        )














