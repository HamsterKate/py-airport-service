from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser

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
    AirplaneCreateSerializer,
    AirplaneSerializer,
    AirplaneTypeImageSerializer,
    AirplaneTypeSerializer,
    AirportCreateSerializer,
    AirportSerializer,
    CrewSerializer,
    DispatcherOrderSerializer,
    FlightCreateUpdateSerializer,
    FlightDispatcherDetailSerializer,
    FlightPublicDetailSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    RouteSerializer,
    FlightListSerializer,
    FlightStaffDetailSerializer,
)

from user.models import User

from airport.permissions import IsCustomerOrDispatcher, IsDispatcherOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="List airplane types",
        description="Retrieve all available airplane types.",
    ),
    retrieve=extend_schema(
        summary="Retrieve airplane type",
        description="Retrieve detailed information about an airplane type.",
    ),
    create=extend_schema(
        summary="Create airplane type",
        description="Create a new airplane type. Available only to dispatchers.",
    ),
)
class AirplaneTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all().order_by("name")
    serializer_class = AirplaneTypeSerializer
    serializer_action_classes = {
        "upload_image": AirplaneTypeImageSerializer,
    }
    permission_classes = (IsDispatcherOrReadOnly,)

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action,
            self.serializer_class,
        )

    @extend_schema(
        summary="Upload airplane type image",
        description="Upload or replace the representative image for an airplane type.",
        request={
            "multipart/form-data": AirplaneTypeImageSerializer,
        },
        responses=AirplaneTypeImageSerializer,
    )
    @action(
        methods=["post"],
        detail=True,
        parser_classes=[MultiPartParser],
        url_path="upload-image",
    )
    def upload_image(
        self,
        request: Request,
        pk: int | None = None
    ) -> Response:
        airplane_type = self.get_object()

        serializer = self.get_serializer(
            airplane_type,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List crew members",
        description="Retrieve a list of all crew members.",
    ),
    retrieve=extend_schema(
        summary="Retrieve crew member",
        description="Retrieve detailed information about a crew member.",
    ),
    create=extend_schema(
        summary="Create crew member",
        description="Create a new crew member. Dispatcher only.",
    ),
)
class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all().order_by("last_name", "first_name")
    serializer_class = CrewSerializer
    search_fields = (
        "first_name",
        "last_name",
    )


@extend_schema_view(
    list=extend_schema(
        summary="List airports",
        description="Retrieve a list of all airports.",
    ),
    retrieve=extend_schema(
        summary="Retrieve airport",
        description="Retrieve detailed information about a single airport.",
    ),
    create=extend_schema(
        summary="Create airport",
        description="Create a new airport. Dispatcher only.",
        request=AirportCreateSerializer,
        responses=AirportSerializer
    ),
)
class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.select_related(
        "city",
        "city__country",
    ).order_by("name")
    serializer_class = AirportSerializer
    serializer_action_classes = {
        "create": AirportCreateSerializer
    }
    search_fields = (
        "name",
        "city__name",
        "city__country__name",
    )

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action,
            self.serializer_class
        )


@extend_schema_view(
    list=extend_schema(
        summary="List airplanes",
        description="Retrieve a list of all airplanes.",
    ),
    retrieve=extend_schema(
        summary="Retrieve airplane",
        description="Retrieve detailed information about a single airplane.",
    ),
    create=extend_schema(
        summary="Create airplane",
        description="Create a new airplane. Dispatcher only.",
        request=AirplaneCreateSerializer,
        responses=AirplaneSerializer
    ),
)
class AirplaneViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = (
        Airplane.objects
        .select_related("airplane_type")
        .order_by("name")
    )
    serializer_class = AirplaneSerializer
    serializer_action_classes = {
        "create": AirplaneCreateSerializer,
    }
    filterset_fields = ("airplane_type",)
    search_fields = ("name", "registration_number")
    ordering_fields = ("name", "registration_number")

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action,
            self.serializer_class,
        )


@extend_schema_view(
    list=extend_schema(
        summary="List routes",
        description="Retrieve a list of all flight routes.",
    ),
    retrieve=extend_schema(
        summary="Retrieve route",
        description="Retrieve detailed information about a single flight route.",
    ),
    create=extend_schema(
        summary="Create route",
        description="Create a new flight route. Dispatcher only.",
    ),
)
class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.select_related(
        "source",
        "source__city",
        "source__city__country",
        "destination",
        "destination__city",
        "destination__city__country",
    ).order_by(
        "source__name",
        "destination__name",
    )
    serializer_class = RouteSerializer
    filterset_class = RouteFilter
    search_fields = (
        "source__name",
        "destination__name",
        "source__city__name",
        "destination__city__name",
    )
    ordering_fields = ("source__name", "destination__name")


@extend_schema_view(
    list=extend_schema(
        summary="List flights",
        description=(
            "Retrieve a list of scheduled flights. "
            "Supports filtering, searching, and ordering."
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve flight",
        description=(
            "Retrieve detailed information about a flight. "
            "The response depends on the authenticated user's role."
        ),
    ),
    create=extend_schema(
        summary="Create flight",
        description="Create a new flight. Dispatcher only.",
    ),
)
class FlightViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = (
        Flight.objects.select_related(
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
        "airplane__registration_number",
    )
    ordering_fields = ("departure_time", "arrival_time", "flight_number")

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        role_serializer_classes = {
            User.Roles.DISPATCHER: FlightDispatcherDetailSerializer,
            User.Roles.CREW: FlightStaffDetailSerializer,
        }

        if self.action == "retrieve":
            user = self.request.user

            return role_serializer_classes.get(user.role, FlightPublicDetailSerializer)

        return FlightCreateUpdateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List orders",
        description=(
            "Retrieve orders. "
            "Customers can view only their own orders, "
            "while dispatchers can view all orders."
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve order",
        description=(
            "Retrieve detailed information about an order. "
            "Customers can access only their own orders, "
            "while dispatchers can access any order."
        ),
    ),
    create=extend_schema(
        summary="Create order",
        description=(
            "Create a new ticket order. "
            "Available to authenticated customers and dispatchers."
        ),
    ),
)
class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.select_related("user").prefetch_related(
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
    permission_classes = (IsCustomerOrDispatcher,)
    filterset_fields = ("user",)
    ordering_fields = ("created_at",)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        if user.is_superuser or user.role == User.Roles.DISPATCHER:
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
