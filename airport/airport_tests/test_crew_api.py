from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from airport.models import Crew
from airport.airport_tests.helpers import create_crew
from user.user_tests.helpers import create_dispatcher, create_user


CREW_URL = reverse("airport:crew-list")


def detail_url(crew_id: int) -> str:
    return reverse(
        "airport:crew-detail",
        args=[crew_id],
    )


class PublicCrewApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_crew(self):
        create_crew(first_name="John")
        create_crew(first_name="Kate")

        res = self.client.get(CREW_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(res.data), 2)

    def test_retrieve_crew(self):
        crew = create_crew()

        res = self.client.get(detail_url(crew.id))

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            res.data["id"],
            crew.id,
        )

    def test_create_requires_authentication(self):
        payload = {
            "first_name": "New",
            "last_name": "Pilot",
        }

        res = self.client.post(
            CREW_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class PrivateCrewApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_customer_cannot_create_crew(self):
        payload = {
            "first_name": "New",
            "last_name": "Pilot",
        }

        res = self.client.post(
            CREW_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_customer_can_list_crew(self):
        create_crew()

        res = self.client.get(CREW_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )


class DispatcherCrewApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.dispatcher = create_dispatcher()
        self.client.force_authenticate(self.dispatcher)

    def test_dispatcher_can_create_crew(self):
        payload = {
            "first_name": "Kate",
            "last_name": "Wilson",
        }

        res = self.client.post(
            CREW_URL,
            payload,
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Crew.objects.filter(
                first_name="Kate",
                last_name="Wilson",
            ).exists()
        )

    def test_search_crew(self):
        create_crew(
            first_name="John",
            last_name="Smith",
        )
        create_crew(
            first_name="Kate",
            last_name="Brown",
        )

        res = self.client.get(
            CREW_URL,
            {"search": "John"},
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(res.data),
            1,
        )
        self.assertEqual(
            res.data[0]["first_name"],
            "John",
        )

    def test_crew_are_ordered_by_last_name(self):
        create_crew(
            first_name="John",
            last_name="Zulu",
        )
        create_crew(
            first_name="Kate",
            last_name="Alpha",
        )

        res = self.client.get(CREW_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            res.data[0]["last_name"],
            "Alpha",
        )   









