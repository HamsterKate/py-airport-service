import django_filters

from airport.models import (
    Flight, Route
)

class FlightFilter(django_filters.FilterSet):
    departure_date = django_filters.DateFilter(
        field_name="departure_time",
        lookup_expr="date",
    )

    departure_after = django_filters.DateTimeFilter(
        field_name="departure_time",
        lookup_expr="gte",
    )

    departure_before = django_filters.DateTimeFilter(
        field_name="departure_time",
        lookup_expr="lte",
    )

    class Meta:
        model = Flight
        fields = (
            "status",
            "route",
            "airplane",
        )


class RouteFilter(django_filters.FilterSet):
   
    class Meta:
        model = Route
        fields = (
            "source",
            "destination",
        )
