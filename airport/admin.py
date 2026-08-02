from django.contrib import admin
from django.db.models import QuerySet

from airport.models import (
    Airplane, AirplaneType, Airport, Crew, Flight, Route
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "closest_big_city",
    )
    ordering = ("name",)
    search_fields = ("name", "closest_big_city")


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)
    search_fields = ("name",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "airplane_type",
        "rows",
        "seats_in_row",
        "capacity",
    )
    ordering = ("name",)
    search_fields = ("name", "airplane_type__name")
    list_filter = ("airplane_type",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    ordering = (
        "source__name",
        "destination__name",
    )
    search_fields = (
        "source__name",
        "source__closest_big_city",
        "destination__name",
        "destination__closest_big_city",
    )
    list_filter = ("source", "destination")


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    ordering = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")
    list_filter = ("first_name", "last_name")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):

    @admin.display(description="Crew")
    def crew_members(self, obj: Flight) -> str:
        return ", ".join(
            str(member)
            for member in obj.crew.all()
        )

    def get_queryset(self, request) -> QuerySet:
        queryset = super().get_queryset(request)

        return (
            queryset
            .select_related(
                "route",
                "route__source",
                "route__destination",
                "airplane",
            )
            .prefetch_related("crew")
        )

    list_display = (
        "route",
        "airplane",
        "departure_time",
        "arrival_time",
        "duration",
        "crew_members",
    )
    ordering = ("departure_time",)
    search_fields = (
        "route__source__name",
        "route__source__closest_big_city",
        "route__destination__name",
        "route__destination__closest_big_city",
        "airplane__name"
    )
    list_filter = (
        "route",
        "airplane"
    )

