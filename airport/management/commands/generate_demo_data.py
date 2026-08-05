import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from airport.demo_data import (
    AIRPLANES,
    AIRPLANE_TYPES,
    AIRPORTS,
    CITIES,
    COUNTRIES,
    CREW_MEMBERS,
    DEMO_PASSWORD,
    ROUTES,
    USERS,
)
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

User = get_user_model()

ROLE_MAP = {
    "dispatcher": User.Roles.DISPATCHER,
    "crew": User.Roles.CREW,
    "customer": User.Roles.CUSTOMER,
}

class Command(BaseCommand):
    help = "Generate demo data for Airport API"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Demo data generation started...")
        )

        self.clear_database()

        self.create_countries()
        self.create_cities()
        self.create_airports()
        self.create_airplane_types()
        self.create_airplanes()
        self.create_crew()
        self.create_routes()
        self.create_flights()

        self.create_users()
        self.create_orders()
        self.create_tickets()

        self.stdout.write(
            self.style.SUCCESS("Demo data generated successfully!")
        )

        self.stdout.write(
            self.style.WARNING(
                f"All demo users password: {DEMO_PASSWORD}"
            )
        )

    def clear_database(self):
        self.stdout.write("Clearing database...")

        Ticket.objects.all().delete()
        Order.objects.all().delete()
        Flight.objects.all().delete()
        Route.objects.all().delete()
        Crew.objects.all().delete()
        Airplane.objects.all().delete()
        AirplaneType.objects.all().delete()
        Airport.objects.all().delete()
        City.objects.all().delete()
        Country.objects.all().delete()

        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(
            self.style.SUCCESS("✓ Database cleared")
        )

    def create_countries(self):
        self.stdout.write("Creating countries...")

        Country.objects.bulk_create(
            [
                Country(name=name, code=code)
                for name, code in COUNTRIES
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {Country.objects.count()} countries"
            )
        )

    def create_cities(self):
        self.stdout.write("Creating cities...")

        countries = {
            country.code: country
            for country in Country.objects.all()
        }

        City.objects.bulk_create(
            [
                City(
                    name=name,
                    country=countries[country_code],
                )
                for name, country_code in CITIES
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {City.objects.count()} cities"
            )
        )

    def create_airports(self):
        self.stdout.write("Creating airports...")

        cities = {
            city.name: city
            for city in City.objects.all()
        }

        Airport.objects.bulk_create(
            [
                Airport(
                    name=airport_name,
                    city=cities[city_name],
                    closest_big_city=closest_big_city,
                )
                for (
                    airport_name,
                    city_name,
                    closest_big_city,
                ) in AIRPORTS
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {Airport.objects.count()} airports"
            )
        )

    def create_airplane_types(self):
        self.stdout.write("Creating airplane types...")

        AirplaneType.objects.bulk_create(
            [
                AirplaneType(name=name)
                for name in AIRPLANE_TYPES
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {AirplaneType.objects.count()} airplane types"
            )
        )

    def create_airplanes(self):
        self.stdout.write("Creating airplanes...")

        airplane_types = {
            airplane_type.name: airplane_type
            for airplane_type in AirplaneType.objects.all()
        }

        Airplane.objects.bulk_create(
            [
                Airplane(
                    name=name,
                    registration_number=registration,
                    airplane_type=airplane_types[type_name],
                    rows=rows,
                    seats_in_row=seats,
                )
                for (
                    name,
                    registration,
                    type_name,
                    rows,
                    seats,
                ) in AIRPLANES
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {Airplane.objects.count()} airplanes"
            )
        )

    def create_crew(self):
        self.stdout.write("Creating crew members...")

        Crew.objects.bulk_create(
            [
                Crew(
                    first_name=first_name,
                    last_name=last_name,
                )
                for first_name, last_name in CREW_MEMBERS
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {Crew.objects.count()} crew members"
            )
        )

    def create_routes(self):
        self.stdout.write("Creating routes...")

        airports = {
            airport.closest_big_city: airport
            for airport in Airport.objects.all()
        }

        Route.objects.bulk_create(
            [
                Route(
                    source=airports[source],
                    destination=airports[destination],
                    distance=distance,
                )
                for source, destination, distance in ROUTES
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {Route.objects.count()} routes"
            )
        )

    def create_flights(self):
        self.stdout.write("Creating flights...")

        routes = list(Route.objects.all())
        airplanes = list(Airplane.objects.all())
        crew_members = list(Crew.objects.all())

        base_time = timezone.now()

        airlines = [
            "PS",  # Ukraine
            "BA",  # British Airways
            "AF",  # Air France
            "KL",  # KLM
            "LH",  # Lufthansa
            "LO",  # LOT
            "JL",  # Japan Airlines
            "AA",  # American Airlines
        ]

        statuses = [
            Flight.Status.SCHEDULED,
            Flight.Status.SCHEDULED,
            Flight.Status.SCHEDULED,
            Flight.Status.BOARDING,
            Flight.Status.DELAYED,
            Flight.Status.DEPARTED,
            Flight.Status.ARRIVED,
        ]

        terminals = ["A", "B", "C", "D"]

        created = 0

        for i, route in enumerate(routes):
            for j in range(2):
                departure = base_time + timedelta(
                    days=i,
                    hours=j * 6,
                )

                duration = random.randint(2, 12)

                arrival = departure + timedelta(hours=duration)

                flight = Flight.objects.create(
                    route=route,
                    airplane=random.choice(airplanes),
                    departure_time=departure,
                    arrival_time=arrival,
                    flight_number=(
                        f"{random.choice(airlines)}"
                        f"{100 + i * 2 + j}"
                    ),
                    status=random.choice(statuses),
                    terminal=random.choice(terminals),
                    gate=(
                        f"{random.choice(terminals)}"
                        f"{random.randint(1, 30)}"
                    ),
                )

                flight.crew.set(
                    random.sample(crew_members, k=5)
                )

                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {created} flights"
            )
        )

    def create_users(self):
        self.stdout.write("Creating users...")

        for email, first_name, last_name, role in USERS:
            User.objects.create_user(
                email=email,
                password=DEMO_PASSWORD,
                first_name=first_name,
                last_name=last_name,
                role=ROLE_MAP[role],
                is_staff=(role == "dispatcher"),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {User.objects.filter(is_superuser=False).count()} users"
            )
        )

    def create_orders(self):
        self.stdout.write("Creating orders...")

        users = list(
            User.objects.filter(
                role=User.Roles.CUSTOMER
            )
        )

        orders = []

        for user in users:
            for _ in range(random.randint(1, 3)):
                orders.append(Order(user=user))

        Order.objects.bulk_create(orders)

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {Order.objects.count()} orders"
            )
        )

    def create_tickets(self):
        self.stdout.write("Creating tickets...")

        flights = list(Flight.objects.all())
        orders = list(Order.objects.all())

        created = 0

        for order in orders:
            flight = random.choice(flights)
            airplane = flight.airplane

            taken = set(
                Ticket.objects.filter(
                    flight=flight
                ).values_list(
                    "row",
                    "seat",
                )
            )

            tickets_amount = random.randint(1, 3)

            for _ in range(tickets_amount):
                attempts = 0

                while attempts < 50:
                    row = random.randint(
                        1,
                        airplane.rows,
                    )

                    seat = random.randint(
                        1,
                        airplane.seats_in_row,
                    )

                    if (row, seat) not in taken:
                        Ticket.objects.create(
                            order=order,
                            flight=flight,
                            row=row,
                            seat=seat,
                        )

                        taken.add((row, seat))
                        created += 1
                        break

                    attempts += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {created} tickets"
            )
        )








