from rest_framework import viewsets

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Route,
)
from airport.serializers import (
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    CrewSerializer,
    RouteSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = (
        Airplane.objects
        .select_related("airplane_type")
    )
    serializer_class = AirplaneSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = (
        Route.objects
        .select_related("source", "destination")
    )
    serializer_class = RouteSerializer