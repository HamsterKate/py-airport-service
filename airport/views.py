from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

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
    FlightPublicDetailSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    RouteSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightStaffDetailSerializer,
    FlightCreateSerializer,
)


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


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


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


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = (
        Route.objects
        .select_related("source", "destination")
    )
    serializer_class = RouteSerializer


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
            "route__destination",
            "airplane",
            "airplane__airplane_type",
        )
        .prefetch_related("crew")
    )

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            if (
                self.request.user.is_authenticated
                and self.request.user.is_staff
            ):
                return FlightStaffDetailSerializer

            return FlightPublicDetailSerializer

        if self.action == "create":
            return FlightCreateSerializer

        return FlightSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        queryset = (
            Order.objects
            .prefetch_related(
                "tickets",
                "tickets__flight",
            )
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer

        return OrderSerializer
