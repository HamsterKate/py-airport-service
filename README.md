# ✈️ Airport Management API

A RESTful API for managing airport operations, including airports, routes, flights, airplanes, crew members, tickets, orders, and users.

The project is built with **Django REST Framework** and uses **PostgreSQL** as the database. The application is fully containerized with **Docker Compose**.

---

## 🚀 Features

* Airport management
* Country and city management
* Airplane type management
* Airplane fleet management
* Crew management
* Route management
* Flight management
* Ticket management
* Order management
* User registration and authentication
* JWT authentication
* Role-based access control
* Filtering, searching, and ordering
* Swagger / OpenAPI documentation
* Demo data generation
* Airplane type image uploads
* PostgreSQL database
* Dockerized development environment
* Automated database readiness check
* 82 automated API tests

---

## 🛠 Technologies

* **Python 3.12**
* **Django 6.0.7**
* **Django REST Framework 3.17.1**
* **PostgreSQL 16**
* **Docker / Docker Compose**
* **Simple JWT**
* **drf-spectacular**
* **django-filter**
* **Pillow**
* **psycopg2-binary**

---

## 📁 Project Structure

```text
py-airport-service/
│
├── airport/
│   ├── management/
│   │   └── commands/
│   │       ├── generate_demo_data.py
│   │       └── wait_for_db.py
│   │
│   ├── migrations/
│   ├── airport_tests/
│   ├── admin.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── airport_service/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── user/
│   ├── migrations/
│   ├── user_tests/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── media_seed/
│   └── airplane_types/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── README.md
```

---

# 🐳 Docker Setup

Docker Compose is the recommended way to run the project.

The application consists of two services:

* `app` — Django REST API
* `db` — PostgreSQL 16 database

Docker Compose also creates persistent volumes for:

* PostgreSQL data
* uploaded media
* collected static files

```text
app
 │
 ├── Django
 ├── DRF
 └── JWT
      │
      ▼
    PostgreSQL
```

---

## ⚙️ Environment Variables

Create a local `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Example:

```env
SECRET_KEY=change-me
DEBUG=1

POSTGRES_DB=airport
POSTGRES_USER=airport
POSTGRES_PASSWORD=airport
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Important

The `.env` file is **not committed to Git**.

Only `.env.example` is included in the repository.

---

# ▶️ Running with Docker

### 1. Build the application

```bash
docker compose build
```

### 2. Start the services

```bash
docker compose up
```

The application automatically:

1. waits for PostgreSQL;
2. applies migrations;
3. collects static files;
4. starts the Django development server.

The API will be available at:

```text
http://localhost:8000/
```

When running in GitHub Codespaces, use the forwarded port URL provided by Codespaces.

---

## 🛑 Stop the application

Press:

```text
Ctrl + C
```

or run:

```bash
docker compose down
```

---

## 🔄 Rebuild after code changes

```bash
docker compose up --build
```

---

# 🗄 Database

The project uses PostgreSQL 16.

The database is configured through environment variables:

```env
POSTGRES_DB=airport
POSTGRES_USER=airport
POSTGRES_PASSWORD=airport
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

The PostgreSQL data is stored in the Docker volume:

```text
postgres_data
```

Therefore, restarting containers does not remove the database data.

To remove containers **and database data**:

```bash
docker compose down -v
```

> ⚠️ This removes Docker volumes, including the PostgreSQL database.

---

# 🔧 Database Management

Migrations are applied automatically when the `app` container starts:

```bash
python manage.py migrate
```

Inside the running container, migrations can also be executed manually:

```bash
docker compose exec app python manage.py migrate
```

Create new migrations:

```bash
docker compose exec app python manage.py makemigrations
```

---

# ❤️ Database Health Check

The PostgreSQL service has a Docker health check:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
```

The Django application waits until PostgreSQL becomes available before running migrations.

This is handled by the custom management command:

```bash
python manage.py wait_for_db
```

Example output:

```text
Waiting for database...
Database available!
```

---

# 🌱 Demo Data

The project includes a custom command for generating demo data.

Run:

```bash
docker compose exec app python manage.py generate_demo_data
```

The command creates:

* countries
* cities
* airports
* airplane types
* airplanes
* crew members
* routes
* flights
* users
* orders
* tickets

Example output:

```text
Demo data generation started...
Clearing database...
✓ Database cleared
Creating countries...
✓ Created 8 countries
Creating cities...
✓ Created 8 cities
Creating airports...
✓ Created 8 airports
Creating airplane types...
✓ Created 6 airplane types
Creating airplanes...
✓ Created 10 airplanes
Creating crew members...
✓ Created 20 crew members
Creating routes...
✓ Created 20 routes
Creating flights...
✓ Created 40 flights
Creating users...
✓ Created 8 users
Creating orders...
✓ Created 14 orders
Creating tickets...
✓ Created 31 tickets
Demo data generated successfully!
```

The command also uses images from:

```text
media_seed/airplane_types/
```

to populate airplane type images.

The demo users are created with the password:

```text
demo12345
```

---

# 🖼 Media Files

Uploaded media files are stored in:

```text
/media
```

Docker Compose uses a persistent volume:

```yaml
media_data:/app/media
```

This prevents uploaded files from disappearing when the application container is recreated.

Seed images used by the demo data generator are stored separately:

```text
media_seed/airplane_types/
```

These files are part of the project source code and are **not** stored in the runtime `media` volume.

---

# 📦 Static Files

Django static files are collected into:

```text
/app/static
```

The project uses a persistent Docker volume:

```yaml
static_data:/app/static
```

Static files are collected automatically during container startup:

```bash
python manage.py collectstatic --noinput
```

---

# 🔐 Authentication

The API uses **JWT authentication** with `djangorestframework-simplejwt`.

JWT access tokens expire after:

```text
30 minutes
```

Refresh tokens expire after:

```text
7 days
```

Authentication endpoints are available under:

```text
/api/user/
```

Typical JWT flow:

```text
Register/Login
     │
     ▼
Access + Refresh tokens
     │
     ▼
Authorization: Bearer <access_token>
     │
     ▼
Protected API endpoints
```

---

# 👥 User Roles

The API supports role-based access control.

### Anonymous users

Can access public/read-only information.

### Customer

Can:

* authenticate;
* create orders;
* view and manage their own orders.

### Crew

Can access flight information with additional crew-related details where permitted.

### Dispatcher

Can manage airport-related operational data, including flights.

### Admin

Has full administrative access through Django Admin and API permissions.

---

# 🔑 API Authentication Header

For protected endpoints, send the JWT access token using:

```http
Authorization: Bearer <access_token>
```

---

# 📚 API Documentation

The project uses **drf-spectacular** to generate OpenAPI documentation.

### Swagger UI

```text
/api/docs/
```

### OpenAPI schema

```text
/api/schema/
```

Open Swagger UI in the browser:

```text
http://localhost:8000/api/docs/
```

---

# 🌐 API Endpoints

Main API endpoints:

| Resource       | Endpoint                       |
| -------------- | ------------------------------ |
| Airplane types | `/api/airport/airplane-types/` |
| Crew           | `/api/airport/crews/`          |
| Airports       | `/api/airport/airports/`       |
| Airplanes      | `/api/airport/airplanes/`      |
| Routes         | `/api/airport/routes/`         |
| Flights        | `/api/airport/flights/`        |
| Orders         | `/api/airport/orders/`         |
| Users          | `/api/user/`                   |

The complete API schema and available operations can be explored through Swagger UI.

---

# 🔎 Filtering, Searching & Ordering

The API supports:

* filtering with `django-filter`;
* searching with DRF `SearchFilter`;
* ordering with DRF `OrderingFilter`.

For example:

```text
/api/airport/flights/?search=Kyiv
```

or:

```text
/api/airport/flights/?ordering=departure_time
```

Exact available parameters depend on the endpoint.

---

# 🧪 Tests

The project contains automated tests for the API.

Run the complete test suite inside Docker:

```bash
docker compose exec app python manage.py test
```

Current test suite:

```text
Found 82 test(s).

..................................................................................

Ran 82 tests in 22.706s

OK
```

The tests cover:

* users;
* airplane types;
* airplanes;
* airports;
* crew;
* routes;
* flights;
* orders;
* authentication;
* permissions;
* filtering;
* API behavior.

---

# 🧑‍💻 Local Development Without Docker

Docker is the recommended setup, but the project can also be run locally with a Python virtual environment.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

A local PostgreSQL instance is required when using the Docker-oriented settings.

Then run:

```bash
python manage.py migrate
python manage.py runserver
```

---

# 🛡️ Permissions

The project uses custom DRF permissions for role-based access control.

The default API permission is:

```python
airport.permissions.IsDispatcherOrReadOnly
```

This allows public read access where appropriate while restricting modification operations to authorized users.

Specific viewsets can override the default permissions when necessary.

---

# 🛠 Django Admin

Django Admin is available at:

```text
/admin/
```

Create a superuser with:

```bash
docker compose exec app python manage.py createsuperuser
```

Then open:

```text
http://localhost:8000/admin/
```

---

# 📌 Useful Docker Commands

### Check running containers

```bash
docker compose ps
```

### View application logs

```bash
docker compose logs app
```

### View database logs

```bash
docker compose logs db
```

### Follow application logs

```bash
docker compose logs -f app
```

### Open a shell inside the application

```bash
docker compose exec app bash
```

### Run Django shell

```bash
docker compose exec app python manage.py shell
```

### Run tests

```bash
docker compose exec app python manage.py test
```

### Stop containers

```bash
docker compose down
```

### Stop containers and remove volumes

```bash
docker compose down -v
```

### Rebuild the application

```bash
docker compose build
```

---

# 🐳 Docker Volumes

The project uses three persistent Docker volumes:

| Volume          | Purpose                       |
| --------------- | ----------------------------- |
| `postgres_data` | PostgreSQL database           |
| `media_data`    | Uploaded media                |
| `static_data`   | Collected Django static files |

These volumes are defined in `docker-compose.yml`.

---

# 🔒 Security Notes

For development, `.env` contains local credentials and must not be committed.

The repository provides:

```text
.env.example
```

as a template.

For production deployment, you should additionally:

* generate a strong secret key;
* set `DEBUG=0`;
* configure production `ALLOWED_HOSTS`;
* use secure database credentials;
* configure HTTPS;
* use a production WSGI/ASGI server;
* configure a proper static/media serving strategy.

---

# 📜 License

This project is intended as a learning and portfolio project.

---

# 👩‍💻 Author

**HamsterKate**

GitHub:

```text
https://github.com/HamsterKate
```

Repository:

```text
https://github.com/HamsterKate/py-airport-service
```
