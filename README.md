# Jobs API Microservice (FastAPI)

A lightweight FastAPI microservice for listing and managing job postings with PostgreSQL database support. Payloads are validated with the Pydantic models published in [`jobs-data-contracts`](https://pypi.org/project/jobs-data-contracts/) and follow the canonical OpenAPI schema stored at `schemas/jobs/openapi.yaml`.

## Project Structure

```
Jobs-API-Microservice
├── app
│   ├── __init__.py
│   ├── main.py                # FastAPI app and router mounting
│   ├── database.py            # Database configuration
│   ├── models.py              # SQLAlchemy models
│   └── api
│       └── v1
│           └── jobs.py        # Jobs routes + Pydantic models
├── scripts
│   └── seed_db.py            # Database seeding script
├── Dockerfile                 # Docker image for API
├── docker-compose.yml         # Local development with Docker
├── .env.example              # Environment variables template
├── pyproject.toml
├── requirements.txt
└── README.md
```

The OpenAPI source of truth for this service is kept in `schemas/jobs/openapi.yaml`.

## Database Configuration

This application supports two database configurations:

- **Local Development**: PostgreSQL in Docker (via docker-compose)
- **Other Environments**: AWS RDS PostgreSQL (via environment variables)

The application uses the `DATABASE_URL` environment variable to connect to the database, making it easy to switch between environments.

## Setup Options

### Option 1: Docker (Recommended for Local Development)

This setup runs both the API and PostgreSQL database in Docker containers with persistent storage.

1) Clone the repository

```bash
git clone <repository-url>
cd Jobs-API-Microservice
```

2) Start the services with Docker Compose

```bash
docker-compose up -d
```

This will:
- Start a PostgreSQL database on port 5432 with persistent volume
- Build and start the API on port 8000
- Run Alembic migrations (`alembic upgrade head`) before the API starts

3) (Optional) Seed the database with sample data

```bash
docker-compose exec api python scripts/seed_db.py
```

4) Access the API

- API: http://localhost:8000
- Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- Database: localhost:5432 (credentials in docker-compose.yml)

5) Stop the services

```bash
docker-compose down
```

To remove the database volume (deletes all data):

```bash
docker-compose down -v
```

### Option 2: Local Python Setup (without Docker)

This setup requires a separate PostgreSQL instance.

1) Clone and enter the repo

```bash
git clone <repository-url>
cd Jobs-API-Microservice
```

2) Install dependencies (optionally in a virtualenv)

```bash
pip install -r requirements.txt
```

3) Set up database connection

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```
DATABASE_URL=postgresql://username:password@localhost:5432/jobsdb
```

4) Run database migrations

```bash
alembic upgrade head
```

5) Run the service

```bash
uvicorn app.main:app --reload
```

The app will be available at `http://127.0.0.1:8000`.

6) (Optional) Seed the database

```bash
python scripts/seed_db.py
```

## Deploying to AWS RDS

For staging/production environments using AWS RDS:

1) Create an RDS PostgreSQL instance in AWS

2) Set the `DATABASE_URL` environment variable in your deployment environment:

```bash
export DATABASE_URL=postgresql://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/jobsdb
```

For AWS services like ECS, Lambda, or Elastic Beanstalk, set this as an environment variable in the service configuration.

3) Run database migrations

```bash
alembic upgrade head
```

4) Deploy your application

The application will automatically:
- Connect to the RDS instance using the DATABASE_URL
- Use connection pooling for optimal performance

### Security Notes for AWS RDS

- Use AWS Secrets Manager or Parameter Store for database credentials
- Configure RDS security groups to allow connections only from your application
- Enable SSL/TLS for database connections in production
- Use IAM database authentication when possible

## API Overview

Current routes are mounted without a version prefix (base path is `/`). Endpoints exposed by `app/api/v1/jobs.py`:

- GET `/` — basic service info and a pointer to `/docs`
- GET `/health` — returns `{ "status": "ok", "db": "ok|unavailable" }`
- GET `/jobs` — list all jobs (returns `JobSummary` items)
- POST `/jobs` — create a new job (validated with `jobs-data-contracts` `JobCreate` + `datePosted`)
- GET `/jobs/{externalId}` — fetch a single job by `externalId`
- PUT `/jobs/{externalId}` — replace a job; body `externalId` must match the path parameter
- PATCH `/jobs/{externalId}` — partial update; `externalId` cannot be modified

If you prefer versioned paths (e.g., `/api/v1/jobs`), add a prefix when including the router in `app/main.py`.

## Data Model

The canonical schema is defined in `schemas/jobs/openapi.yaml` and the Pydantic models from the `jobs-data-contracts` package. Complex fields (locations, salary, contacts, attachments) are stored as JSON/JSONB in the database.

## Quick Start (cURL)

- Health check

```bash
curl -s http://127.0.0.1:8000/health | jq
```

- Root landing page

```bash
curl -s http://127.0.0.1:8000/ | jq
```

- List jobs

```bash
curl -s "http://127.0.0.1:8000/jobs" | jq
```

- Create a job

```bash
curl -s -X POST "http://127.0.0.1:8000/jobs" \
   -H "Content-Type: application/json" \
   -d '{
      "externalId": "ext-123",
      "approach": "external",
      "title": "Backend Engineer",
      "description": "Build APIs with FastAPI.",
      "organisation": "Acme Corp",
      "location": [{
        "townName": "London",
        "region": "London",
        "latitude": 51.5,
        "longitude": -0.1
      }],
      "grade": "grade_7",
      "assignmentType": "permanent",
      "workLocation": ["office_based"],
      "workingPattern": ["full_time"],
      "personalSpec": "Python, FastAPI",
      "applyDetail": "Apply online",
      "datePosted": "2025-01-01T00:00:00Z",
      "dateClosing": "2025-02-01T00:00:00Z",
      "profession": "policy",
      "recruitmentEmail": "talent@acme.example"
    }' | jq
```

- Get a job by ID

```bash
curl -s "http://127.0.0.1:8000/jobs/<externalId>" | jq
```

## Queue publishing (SQS)

- The API emits a message to SQS whenever a job is created (POST), replaced (PUT), or updated (PATCH).
- Configure the queue with environment variables:
  - `SQS_QUEUE_URL` (preferred for deployed environments) or `SQS_QUEUE_NAME` + `SQS_ENDPOINT_URL` for local auto-creation.
  - `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
  - Optional: `QUEUE_API_ENDPOINT` (base URL to include in messages), `QUEUE_MESSAGE_VERSION` (defaults to 1).
- `docker-compose` includes a LocalStack SQS service. With the defaults (`SQS_QUEUE_NAME=jobs-api-queue`, `SQS_ENDPOINT_URL=http://localstack:4566`), the queue is created automatically on first use.

## Development

### Docker Development Workflow

The docker-compose setup includes hot-reloading for development:

1. Make changes to files in the `app/` directory
2. The API container will automatically reload
3. View logs: `docker-compose logs -f api`

### Database Management

- Connect to PostgreSQL: `docker-compose exec postgres psql -U jobsapi -d jobsdb`
- View logs: `docker-compose logs postgres`
- Reset database: `docker-compose down -v && docker-compose up -d`

## Environment Variables

| Variable | Description | Default (Local) | Production Example |
|----------|-------------|-----------------|-------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://jobsapi:jobsapi@postgres:5432/jobsdb` | `postgresql://user:pass@rds-endpoint:5432/db` |

## License

MIT
