from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Airplane, AirplaneType, Airport, Crew, Flight, Order, Route, Ticket
)


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name", read_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type"
        )


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.CharField(
        source="source.name", read_only=True
    )
    destination = serializers.CharField(
        source="destination.name", read_only=True
    )

    class Meta:
        model = Route
        fields = (
            "id", "source", "destination", "distance",
        )


class FlightSerializer(serializers.ModelSerializer):
    duration = serializers.DurationField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "duration",
            "crew",
        )


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    airplane = serializers.CharField(
        source="airplane.name",
        read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "duration",
        )


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    crew = CrewSerializer(
        many=True,
        read_only=True
    )
    duration = serializers.DurationField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
            "duration",
        )


class FlightCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = (
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
        )


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
        )


class TicketCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = (
            "row",
            "seat",
            "flight",
        )

    def validate(self, attrs):
        flight = attrs["flight"]

        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            flight.airplane,
            serializers.ValidationError,
        )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True,
        read_only=True
    )
    user = serializers.CharField(
        source="user.email",
        read_only=True
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "user",
            "tickets",
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(
        many=True
    )

    class Meta:
        model = Order
        fields = (
            "tickets",
        )

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")

        user = self.context["request"].user

        with transaction.atomic():
            order = Order.objects.create(
                user=user
            )

            for ticket_data in tickets_data:
                Ticket.objects.create(
                    order=order,
                    **ticket_data
                )

        return order










