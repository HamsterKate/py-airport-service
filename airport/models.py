from datetime import timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import (F, Q)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.name} ({self.closest_big_city})"


class AirplaneType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return f"{self.name} ({self.airplane_type})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_routes"
    )
    distance = models.PositiveIntegerField()

    def clean(self) -> None:
        super().clean()

        if self.source == self.destination:
            raise ValidationError(
                {
                    "destination": (
                        "Destination airport must be different "
                        "from source airport."
                    )
                }
            )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(source=F("destination")),
                name="source_not_equal_destination",
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.source} → {self.destination} ({self.distance} km)"
        )


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    
    crew = models.ManyToManyField(
        Crew,
        related_name="flights"
    )

    @property
    def duration(self) -> timedelta:
        return self.arrival_time - self.departure_time

    def clean(self) -> None:
        super().clean()

        if self.arrival_time <= self.departure_time:
            raise ValidationError(
                {
                    "arrival_time": (
                        "Arrival time must "
                        "be later than departure time."                    )
                }
            )
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(arrival_time__gt=F("departure_time")),
                name="arrival_after_departure",
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.route} - {self.departure_time:%Y-%m-%d %H:%M}"
        )
