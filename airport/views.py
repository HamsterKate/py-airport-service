from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Country,
    Crew,
    Order,
    Route,
    Flight,
)
from airport.serializers import (
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    CountrySerializer,
    CrewSerializer,
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
            "route__source__city",
            "route__source__city__country",
            "route__destination",
            "route__destination__city",
            "route__destination__city__country",
            "airplane",
            "airplane__airplane_type",
        )
        .prefetch_related("crew")
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
