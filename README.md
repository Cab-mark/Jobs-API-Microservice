# Jobs API Microservice (FastAPI)

A lightweight FastAPI microservice for listing and managing job postings. The job schema aligns with the TypeScript interface used in the nextjs_govuk_experiment (see active PR for details).

## Project Structure

```
Jobs-API-Microservice
├── app
│   ├── __init__.py
│   ├── main.py                # FastAPI app and router mounting
│   └── api
│       └── v1
│           └── jobs.py        # Jobs routes + Pydantic models
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Setup

1) Clone and enter the repo

```bash
git clone <repository-url>
cd Jobs-API-Microservice
```

2) Install dependencies (optionally in a virtualenv)

```bash
pip install -r requirements.txt
```

3) Run the service

```bash
uvicorn app.main:app --reload
```

The app will be available at `http://127.0.0.1:8000`.

## API Overview

Current routes are mounted without a version prefix (base path is `/`). Endpoints exposed by `app/api/v1/jobs.py`:

- GET `/jobs` — list all jobs
- POST `/jobs` — create a new job (returns the created job with generated `id`)
- GET `/jobs/{job_id}` — fetch a single job by ID

If you prefer versioned paths (e.g., `/api/v1/jobs`), add a prefix when including the router in `app/main.py`.

## Data Model (summary)

The `Job` model includes (non-exhaustive):

- id, title, description, organisation, location, grade, assignmentType, personalSpec
- Optional: nationalityRequirement, summary, applyUrl, benefits, profession, applyDetail, salary, closingDate, jobNumbers
- contacts (bool), Optional: contactName, contactEmail, contactPhone
- recruitmentEmail

Example job object:

```json
{
   "id": "1567",
   "title": "Policy Advisor",
   "description": "This is a fantastic job for a policy advisor...",
   "organisation": "Ministry of Defence",
   "location": "3 Glass Wharf, Bristol, BS2 OEL",
   "grade": "Grade 7",
   "assignmentType": "Fixed Term Appointment (FTA)",
   "personalSpec": "Some personal specification text",
   "salary": "£45,000",
   "closingDate": "20 December 2025",
   "jobNumbers": 1,
   "contacts": false,
   "recruitmentEmail": "recruitment@civilservice.gov.uk"
}
```

## Quick Start (cURL)

- List jobs

```bash
curl -s "http://127.0.0.1:8000/jobs" | jq
```

- Create a job

```bash
curl -s -X POST "http://127.0.0.1:8000/jobs" \
   -H "Content-Type: application/json" \
   -d '{
      "title": "Backend Engineer",
      "description": "Build APIs with FastAPI.",
      "organisation": "Acme Corp",
      "location": "Remote",
      "grade": "Senior",
      "assignmentType": "Permanent",
      "personalSpec": "Python, FastAPI",
      "salary": "£100,000",
      "contacts": false,
      "recruitmentEmail": "talent@acme.example"
   }' | jq
```

- Get a job by ID

```bash
curl -s "http://127.0.0.1:8000/jobs/<job_id>" | jq
```

## Notes

- Data is currently in-memory for demonstration. Connect a database (e.g., PostgreSQL with SQLAlchemy) for persistence.
- To introduce versioned endpoints, mount the router with a prefix in `app/main.py`, e.g. `app.include_router(jobs_router, prefix="/api/v1")` and update examples accordingly.

## License

MIT