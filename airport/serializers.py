from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    City,
    Country,
    Crew,
    Flight,
    Order,
    Route,
    Ticket
)


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ("id", "name", "code")


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = City
        fields = ("id", "name", "country")


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class AirplaneShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "registration_number",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name", read_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "registration_number",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type"
        )


class AirportSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "city", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField(read_only=True)
    destination = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Route
        fields = (
            "id", "source", "destination", "distance",
        )


class FlightCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Flight
        fields = (
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "flight_number",
            "status",
            "terminal",
            "gate",
            "crew",
        )


class FlightListSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneShortSerializer(read_only=True)
    duration = serializers.DurationField(read_only=True)
    status = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "status",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "duration",
            "terminal",
            "gate",
        )


class FlightTicketSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "route",
            "departure_time",
        )


class FlightPublicDetailSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneShortSerializer(read_only=True)
    duration = serializers.DurationField(read_only=True)
    status = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "duration",
            "status",
            "terminal",
            "gate"
        )


class FlightStaffDetailSerializer(FlightPublicDetailSerializer):
    crew = CrewSerializer(
        many=True,
        read_only=True
    )

    class Meta(FlightPublicDetailSerializer.Meta):
        fields = FlightPublicDetailSerializer.Meta.fields + ("crew",)


class FlightDispatcherDetailSerializer(
    FlightStaffDetailSerializer
):
    airplane = AirplaneSerializer(read_only=True)

    class Meta(FlightStaffDetailSerializer.Meta):
        fields = FlightStaffDetailSerializer.Meta.fields


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightTicketSerializer(read_only=True)

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

    def validate(self, attrs: dict) -> dict:
        flight = attrs["flight"]

        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            flight.airplane,
            serializers.ValidationError,
        )

        return attrs


class UserShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets",
        )


class DispatcherOrderSerializer(OrderSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta(OrderSerializer.Meta):
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

    def create(self, validated_data: dict) -> Order:
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


