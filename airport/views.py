from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from airport.filters import FlightFilter, RouteFilter
from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Order,
    Route,
    Flight,
)
from airport.serializers import (
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    CrewSerializer,
    DispatcherOrderSerializer,
    FlightCreateUpdateSerializer,
    FlightDispatcherDetailSerializer,
    FlightPublicDetailSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    RouteSerializer,
    # FlightSerializer,
    FlightListSerializer,
    FlightStaffDetailSerializer,
    # FlightCreateSerializer,
)

from user.models import User

from airport.permissions import IsCustomerOrDispatcher


class AirplaneTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    search_fields = (
        "first_name",
        "last_name",
    )


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.select_related(
        "city",
        "city__country",
    )
    serializer_class = AirportSerializer
    search_fields = (
        "name",
        "city__name",
        "city__country__name",
    )


class AirplaneViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = (
        Airplane.objects
        .select_related("airplane_type")
    )
    serializer_class = AirplaneSerializer
    filterset_fields = ("airplane_type",)
    search_fields = ("name", "registration_number")
    ordering_fields = ("name",)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = (
        Route.objects
        .select_related(
            "source",
            "source__city",
            "source__city__country",
            "destination",
            "destination__city",
            "destination__city__country"
        )
    )       
    serializer_class = RouteSerializer
    filterset_class = RouteFilter
    search_fields = (
        "source__name",
        "destination__name",
        "source__city__name",
        "destination__city__name"
    )
    ordering_fields = ("source__name", "destination__name")


class FlightViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = (
        Flight.objects
        .select_related(
            "route",
            "route__source",
            "route__source__city",
            "route__source__city__country",
            "route__destination",
            "route__destination__city",
            "route__destination__city__country",
            "airplane",
            "airplane__airplane_type",
        )
        .prefetch_related("crew")
        .order_by("departure_time")
    )
    filterset_class = FlightFilter
    search_fields = (
        "route__source__name",
        "route__source__city__name",
        "route__destination__name",
        "route__destination__city__name",
        "flight_number",
        "airplane__registration_number"
    )
    ordering_fields = (
        "departure_time",
        "arrival_time"
    )

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            user = self.request.user

            if (
                user.is_authenticated
                and user.role == User.Roles.DISPATCHER
            ):
                return FlightDispatcherDetailSerializer

            if (
                user.is_authenticated
                and user.role == User.Roles.CREW
            ):
                return FlightStaffDetailSerializer

            return FlightPublicDetailSerializer

        return FlightCreateUpdateSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related(
            "tickets",
            "tickets__flight",
            "tickets__flight__route",
            "tickets__flight__route__source",
            "tickets__flight__route__source__city",
            "tickets__flight__route__source__city__country",
            "tickets__flight__route__destination",
            "tickets__flight__route__destination__city",
            "tickets__flight__route__destination__city__country",
        )
    )
    permission_classes = (IsCustomerOrDispatcher,)
    filterset_fields = ("user",)
    ordering_fields = ("created_at",)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        if (
            user.is_superuser
            or user.role == User.Roles.DISPATCHER
        ):
            return queryset

        return queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer

        if (
            self.request.user.is_superuser
            or self.request.user.role == User.Roles.DISPATCHER
        ):
            return DispatcherOrderSerializer

        return OrderSerializer
