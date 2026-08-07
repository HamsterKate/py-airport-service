import uuid
from datetime import timedelta

from django.utils import timezone

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    City,
    Country,
    Crew,
    Flight,
    Order,
    Route,
    Ticket,
)

from user.tests.helpers import create_user


def create_country(**params) -> Country:
    number = Country.objects.count()

    defaults = {
        "name": f"Country-{uuid.uuid4().hex[:6]}",
        "code": f"{number:02X}",
    }

    defaults.update(params)

    return Country.objects.create(**defaults)


def create_city(**params) -> City:
    country = params.pop("country", None)

    if country is None:
        country = create_country()

    defaults = {
        "name": f"City-{uuid.uuid4().hex[:6]}",
        "country": country,
    }
    defaults.update(params)

    return City.objects.create(**defaults)


def create_airport(**params) -> Airport:
    city = params.pop("city", None)

    if city is None:
        city = create_city()

    defaults = {
        "name": "Boryspil Airport",
        "city": city,
        "closest_big_city": "Kyiv",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def create_airplane_type(**params) -> AirplaneType:
    defaults = {
        "name": "Boeing 737-800",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def create_airplane(**params) -> Airplane:
    airplane_type = params.pop("airplane_type", None)

    if not airplane_type:
        airplane_type = create_airplane_type(
            name=f"Boeing {Airplane.objects.count() + 737}",
        )

    defaults = {
        "name": "Sky Falcon",
        "registration_number": f"UR-{Airplane.objects.count() + 100}",
        "rows": 30,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }

    defaults.update(params)

    return Airplane.objects.create(**defaults)


def create_crew(**params) -> Crew:
    defaults = {
        "first_name": "John",
        "last_name": "Smith",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def create_route(**params) -> Route:
    source = params.pop("source", None)
    if source is None:
        source = create_airport()

    destination = params.pop("destination", None)
    if destination is None:
        destination = create_airport(
            name="Heathrow Airport",
            closest_big_city="London",
            city=create_city(
                name="London",
                country=create_country(
                    name="United Kingdom",
                    code="GB",
                ),
            ),
        )

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 2200,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def create_flight(**params) -> Flight:
    route = params.pop("route", create_route())
    airplane = params.pop("airplane", create_airplane())

    departure = params.pop("departure_time", timezone.now())
    arrival = params.pop(
        "arrival_time",
        departure + timedelta(hours=2),
    )

    crew = params.pop(
        "crew",
        [create_crew(), create_crew()],
    )

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": departure,
        "arrival_time": arrival,
        "flight_number": "PS101",
    }
    defaults.update(params)

    flight = Flight.objects.create(**defaults)
    flight.crew.set(crew)

    return flight


def create_order(**params) -> Order:
    user = params.pop(
        "user",
        create_user(),
    )

    defaults = {
        "user": user,
    }
    defaults.update(params)

    return Order.objects.create(**defaults)


def create_ticket(**params) -> Ticket:
    flight = params.pop("flight", create_flight())
    order = params.pop("order", create_order())

    defaults = {
        "flight": flight,
        "order": order,
        "row": 1,
        "seat": 1,
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)
