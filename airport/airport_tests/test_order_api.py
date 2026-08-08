from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Order
from airport.airport_tests.helpers import create_flight, create_order
from user.user_tests.helpers import (
    create_user,
    create_dispatcher,
)


User = get_user_model()

ORDER_URL = reverse("airport:order-list")


def detail_url(order_id):
    return reverse("airport:order-detail", args=[order_id])


class CustomerOrderApiTests(APITestCase):

    def setUp(self):
        self.user = create_user(
            role=User.Roles.CUSTOMER,
        )
        self.client.force_authenticate(self.user)

    def test_list_only_own_orders(self):
        own_order = create_order(user=self.user)
        other_user = create_user(
            email="other@example.com"
        )
        create_order(user=other_user)

        res = self.client.get(ORDER_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(res.data),
            1,
        )

        self.assertEqual(
            res.data[0]["id"],
            own_order.id,
        )

    def test_retrieve_own_order(self):
        order = create_order(user=self.user)

        res = self.client.get(
            detail_url(order.id)
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            res.data["id"],
            order.id,
        )

    def test_retrieve_other_users_order(self):
        other_user = create_user(
            email="other@example.com",
        )
        order = create_order(user=other_user)

        res = self.client.get(
            detail_url(order.id)
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_order(self):
        flight = create_flight()

        payload = {
            "tickets": [
                {
                    "flight": flight.id,
                    "row": 1,
                    "seat": 1,
                }
            ]
        }

        res = self.client.post(
            ORDER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(user=self.user)

        self.assertEqual(
            order.user,
            self.user,
        )

        self.assertEqual(
            order.tickets.count(),
            1,
        )

        ticket = order.tickets.first()

        self.assertEqual(
            ticket.flight,
            flight,
        )

        self.assertEqual(
            ticket.order,
            order,
        )

    def test_create_order_with_multiple_tickets(self):
        flight_1 = create_flight(
            flight_number="PS101",
        )
        flight_2 = create_flight(
            flight_number="PS102",
        )

        payload = {
            "tickets": [
                {
                    "flight": flight_1.id,
                    "row": 1,
                    "seat": 1,
                },
                {
                    "flight": flight_2.id,
                    "row": 2,
                    "seat": 3,
                },
            ]
        }

        res = self.client.post(
            ORDER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(user=self.user)

        self.assertEqual(
            order.user,
            self.user,
        )

        self.assertEqual(
            order.tickets.count(),
            2,
        )

        self.assertEqual(
            set(order.tickets.values_list("flight_id", flat=True)),
            {flight_1.id, flight_2.id},
        )

    def test_create_order_invalid_ticket_is_atomic(self):
        flight = create_flight()

        payload = {
            "tickets": [
                {
                    "flight": flight.id,
                    "row": 1,
                    "seat": 1,
                },
                {
                    "flight": flight.id,
                    "row": 999,
                    "seat": 999,
                },
            ]
        }

        res = self.client.post(
            ORDER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

        self.assertEqual(
            flight.tickets.count(),
            0,
        )


class AnonymousOrderApiTests(APITestCase):

    def test_anonymous_cannot_list_orders(self):
        res = self.client.get(ORDER_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_anonymous_cannot_retrieve_order(self):
        order = create_order()

        res = self.client.get(
            detail_url(order.id)
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_anonymous_cannot_create_order(self):
        res = self.client.post(
            ORDER_URL,
            {"tickets": []},
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class DispatcherOrderApiTests(APITestCase):

    def setUp(self):
        self.dispatcher = create_dispatcher()
        self.client.force_authenticate(self.dispatcher)

    def test_dispatcher_can_list_all_orders(self):
        customer_1 = create_user(email="customer1@example.com")
        customer_2 = create_user(email="customer2@example.com")

        order_1 = create_order(user=customer_1)
        order_2 = create_order(user=customer_2)

        res = self.client.get(ORDER_URL)

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            {order["id"] for order in res.data},
            {order_1.id, order_2.id},
        )

    def test_dispatcher_can_retrieve_any_order(self):
        customer = create_user(email="customer@example.com")
        order = create_order(user=customer)

        res = self.client.get(
            detail_url(order.id)
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            res.data["id"],
            order.id,
        )

    def test_dispatcher_response_contains_user(self):
        customer = create_user(
            email="customer@example.com",
            first_name="John",
            last_name="Doe",
        )
        order = create_order(user=customer)

        res = self.client.get(
            detail_url(order.id)
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("user", res.data)
        self.assertEqual(
            res.data["user"]["id"],
            customer.id,
        )
        self.assertEqual(
            res.data["user"]["first_name"],
            "John",
        )

        self.assertEqual(
            res.data["user"]["last_name"],
            "Doe",
        )

    def test_dispatcher_can_create_order(self):
        flight = create_flight()

        payload = {
            "tickets": [
                {
                    "flight": flight.id,
                    "row": 1,
                    "seat": 1,
                }
            ]
        }

        res = self.client.post(
            ORDER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get()

        self.assertEqual(
            order.user,
            self.dispatcher,
        )

        self.assertEqual(
            order.tickets.count(),
            1,
        )