from django.db import transactions
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







