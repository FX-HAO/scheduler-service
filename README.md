# Scheduler Service

[![CI](https://github.com/CoCongV/scheduler-service/actions/workflows/ci.yml/badge.svg)](https://github.com/CoCongV/scheduler-service/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/CoCongV/scheduler-service/graph/badge.svg?token=tvuEjqNQss)](https://codecov.io/github/CoCongV/scheduler-service)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/8533c1d0460d4106a7abca744882d209)](https://app.codacy.com/gh/CoCongV/scheduler-service/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

This is a project for providing service based on REST to schedule tasks.
With this you can trigger an action every day of the month, every day of the week or every single day.
You can also select the hour of the day. If you're a developer, this is similar to a crontab, cronjob or cron.

## Tech Stack

- **Web Framework**: FastAPI
- **ORM**: Tortoise-ORM (PostgreSQL)
- **Task Queue**: Dramatiq (Redis)
- **Package Manager**: Poetry

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.14+
- Poetry

### 1. Start Infrastructure

Start PostgreSQL and Redis using Docker:

```bash
# Start Redis
docker run -d --name some-redis -p 6379:6379 redis:7

# Start PostgreSQL
docker run -d --name some-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:latest
```

### 2. Configuration

The application uses `config.toml` in the project root directory for configuration.

Create a `config.toml` with the following content:

```toml
PG_URL = "postgresql://postgres:postgres@localhost:5432/scheduler"
REDIS_URL = "redis://localhost:6379/0"
SECRET_KEY = "your-secret-key"
```

### 3. Install Dependencies

```bash
poetry install
```

> Once installed, the `scheduler` command will be available in your environment (e.g., inside `poetry shell`).

### 4. Run Application

The project includes a convenient CLI tool `scheduler`.

```bash
# Initialize database (automatically sets up Aerich migrations)
scheduler init-db

# Start the web server
scheduler runserver

# Start the task worker (in a separate terminal)
scheduler worker
```

### 5. Database Migrations

This project uses Aerich for database migrations, integrated into the `scheduler` CLI.

- **Initialize Database (First Run):**
  ```bash
  # This is equivalent to scheduler init-db
  scheduler migrate init-db
  ```

- **Create a Migration (After modifying models):**
  ```bash
  scheduler migrate create --name update_some_model
  ```

- **Apply Migrations:**
  ```bash
  scheduler migrate upgrade
  ```

- **View History:**
  ```bash
  scheduler migrate history
  ```

## API Documentation

Once the server is running (defaulting to `http://127.0.0.1:8000`), you can access the interactive API documentation:

*   **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Test APIs directly in your browser)
*   **Redoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (Alternative documentation view)

### Core Endpoints

#### Tasks (`/api/v1/task`)

*   `GET /api/v1/task`: Retrieve all tasks for the current user.
*   `POST /api/v1/task`: Create a new task (supports one-time and cron-scheduled tasks).
*   `GET /api/v1/task/{task_id}`: Retrieve details of a specific task.
*   `DELETE /api/v1/task/{task_id}`: Delete a task (and cancel pending/scheduled jobs).

#### Users (`/api/v1/user`)

*   `POST /api/v1/user`: Register a new user.
*   `GET /api/v1/user/me`: Get current user profile.
*   `PUT /api/v1/user/me`: Update current user profile.
*   `DELETE /api/v1/user/me`: Delete current user account.
*   `POST /api/v1/user/token`: Login to obtain an authentication token.

## Testing

Run the test suite with coverage:

```bash
scheduler test --coverage
```

## Roadmap

- [x] User login required
- [x] Asynchronous tasks (via Dramatiq)
- [x] Continuous integration and deployment
- [x] Deploy with docker