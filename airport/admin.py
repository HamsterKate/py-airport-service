from django.contrib import admin

from airport.models import (
    Airplane, AirplaneType, Airport
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




