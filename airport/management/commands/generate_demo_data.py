import random
from datetime import timedelta

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
    Order,
    Ticket,
)


User = get_user_model()


class Command(BaseCommand):
    help = "Generate demo data for Airport API"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Demo data generation started...")
        )

        self.clear_database()

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
            "All demo users password: demo12345"
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
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(
            self.style.SUCCESS("✓ Database cleared")
        )

    def create_airports(self):
        self.stdout.write("Creating airports...")

        airports = [
            ("Boryspil International Airport", "Kyiv"),
            ("Heathrow Airport", "London"),
            ("Charles de Gaulle Airport", "Paris"),
            ("Amsterdam Schiphol Airport", "Amsterdam"),
            ("Frankfurt Airport", "Frankfurt"),
            ("Warsaw Chopin Airport", "Warsaw"),
            ("John F. Kennedy International Airport", "New York"),
            ("Haneda Airport", "Tokyo"),
        ]

        for name, city in airports:
            Airport.objects.create(
                name=name,
                closest_big_city=city,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {Airport.objects.count()} airports"
            )
        )

    def create_airplane_types(self):
        self.stdout.write("Creating airplane types...")

        airplane_types = [
            "Boeing 737-800",
            "Boeing 777-300ER",
            "Airbus A320",
            "Airbus A321neo",
            "Embraer E190",
            "ATR 72-600",
        ]

        AirplaneType.objects.bulk_create(
            [
                AirplaneType(name=name)
                for name in airplane_types
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {AirplaneType.objects.count()} airplane types"
            )
        )

    def create_airplanes(self):
        self.stdout.write("Creating airplanes...")

        airplane_data = [
            ("UR-PSA", "Boeing 737-800", 30, 6),
            ("UR-PSB", "Boeing 737-800", 30, 6),
            ("UR-UIA", "Boeing 777-300ER", 45, 10),
            ("G-EUOH", "Airbus A320", 30, 6),
            ("G-EUPJ", "Airbus A320", 30, 6),
            ("D-AIHC", "Airbus A321neo", 37, 6),
            ("PH-BXA", "Boeing 737-800", 31, 6),
            ("SP-LRA", "Embraer E190", 25, 4),
            ("SP-LRB", "Embraer E190", 25, 4),
            ("JA812A", "ATR 72-600", 18, 4),
        ]

        airplane_types = {
            airplane_type.name: airplane_type
            for airplane_type in AirplaneType.objects.all()
        }

        Airplane.objects.bulk_create(
            [
                Airplane(
                    name=name,
                    airplane_type=airplane_types[type_name],
                    rows=rows,
                    seats_in_row=seats,
                )
                for name, type_name, rows, seats in airplane_data
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {Airplane.objects.count()} airplanes"
            )
        )

    def create_crew(self):
        self.stdout.write("Creating crew members...")

        crew_members = [
            ("John", "Smith"),
            ("Emma", "Johnson"),
            ("Michael", "Brown"),
            ("Olivia", "Davis"),
            ("William", "Miller"),
            ("Sophia", "Wilson"),
            ("James", "Moore"),
            ("Isabella", "Taylor"),
            ("Benjamin", "Anderson"),
            ("Mia", "Thomas"),
            ("Lucas", "Jackson"),
            ("Charlotte", "White"),
            ("Henry", "Harris"),
            ("Amelia", "Martin"),
            ("Alexander", "Thompson"),
            ("Evelyn", "Garcia"),
            ("Daniel", "Martinez"),
            ("Harper", "Robinson"),
            ("Matthew", "Clark"),
            ("Emily", "Rodriguez"),
        ]

        Crew.objects.bulk_create(
            [
                Crew(
                    first_name=first_name,
                    last_name=last_name,
                )
                for first_name, last_name in crew_members
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

        route_data = [
            ("Kyiv", "London", 2130),
            ("Kyiv", "Warsaw", 690),
            ("Kyiv", "Paris", 2020),
            ("Kyiv", "Frankfurt", 1540),

            ("London", "New York", 5567),
            ("London", "Paris", 344),
            ("London", "Amsterdam", 358),
            ("London", "Frankfurt", 638),

            ("Paris", "Amsterdam", 430),
            ("Paris", "Frankfurt", 478),
            ("Paris", "Warsaw", 1366),

            ("Amsterdam", "Frankfurt", 364),
            ("Amsterdam", "Warsaw", 1094),

            ("Frankfurt", "New York", 6200),
            ("Frankfurt", "Tokyo", 9360),

            ("Warsaw", "Frankfurt", 890),
            ("Warsaw", "London", 1448),

            ("Tokyo", "New York", 10870),
            ("Tokyo", "London", 9560),
            ("New York", "Paris", 5836),
        ]

        Route.objects.bulk_create(
            [
                Route(
                    source=airports[source],
                    destination=airports[destination],
                    distance=distance,
                )
                for source, destination, distance in route_data
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

        flights = []

        for i, route in enumerate(routes):
            for j in range(2):
                departure = base_time + timedelta(
                    days=i,
                    hours=j * 6,
                )

                duration_hours = random.randint(2, 12)

                arrival = departure + timedelta(
                    hours=duration_hours
                )

                flight = Flight.objects.create(
                    route=route,
                    airplane=random.choice(airplanes),
                    departure_time=departure,
                    arrival_time=arrival,
                )

                flight.crew.set(
                    random.sample(crew_members, k=5)
                )

                flights.append(flight)

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {len(flights)} flights"
            )
        )

    def create_users(self):
        self.stdout.write("Creating users...")

        User = get_user_model()

        users_data = [
            ("john@example.com", "John", "Smith"),
            ("emma@example.com", "Emma", "Johnson"),
            ("olivia@example.com", "Olivia", "Brown"),
            ("michael@example.com", "Michael", "Wilson"),
            ("sophia@example.com", "Sophia", "Taylor"),
            ("james@example.com", "James", "Anderson"),
            ("amelia@example.com", "Amelia", "Martin"),
            ("lucas@example.com", "Lucas", "White"),
        ]

        for email, first_name, last_name in users_data:
            User.objects.create_user(
                email=email,
                password="demo12345",
                first_name=first_name,
                last_name=last_name,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {User.objects.filter(is_superuser=False).count()} users"
            )
        )

    def create_orders(self):
        self.stdout.write("Creating orders...")

        users = list(User.objects.filter(is_superuser=False))

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

