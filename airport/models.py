from datetime import timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import (F, Q)
from django.conf import settings


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "countries"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )

    class Meta:
        ordering = ("name", "country__name")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "country"],
                name="unique_city_per_country"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.country.code}"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports"
    ) 
    closest_big_city = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


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

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

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


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return str(self.created_at)


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(
        row, seat, airplane, error_to_raise
    ) -> None:
        for value, field_name, airplane_field in (
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ):
            count_attrs = getattr(airplane, airplane_field)
            if not (1 <= value <= count_attrs):
                raise error_to_raise(
                    {
                        field_name: f"{field_name}"
                        f"number must be in available range: "
                        f"(1, {airplane_field}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        super().clean()

        if self.flight_id is None:
            return

        Ticket.validate_ticket(
            self.row, self.seat, self.flight.airplane, ValidationError
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.flight} "
            f"(row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ["flight", "row", "seat"]
        ordering = ["row", "seat"]
