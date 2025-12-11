"""Script to seed the database with initial job data."""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, engine
from app.models import Base, JobModel

# Sample job data to seed the database
SEED_JOBS = [
    {
        "external_id": "seed-001",
        "approach": "External",
        "title": "Policy Advisor",
        "description": "This is a fantastic job for a policy advisor...",
        "organisation": "Ministry of Defence",
        "location": [
            {
                "townName": "Bristol",
                "region": "South West",
                "latitude": 51.4545,
                "longitude": -2.5879,
            }
        ],
        "grade": "Grade 7",
        "assignment_type": "Permanent",
        "work_location": ["Office based"],
        "working_pattern": ["Full-time"],
        "personal_spec": "Some personal specification text",
        "apply_detail": "Apply via careers portal",
        "date_posted": datetime.now(timezone.utc),
        "closing_date": datetime.now(timezone.utc) + timedelta(days=30),
        "profession": "Policy",
        "recruitment_email": "recruitment@civilservice.gov.uk",
    },
]


def seed_database():
    """Seed the database with initial job data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_count = db.query(JobModel).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} jobs. Skipping seed.")
            return

        print("Seeding database with initial job data...")
        for job_data in SEED_JOBS:
            job = JobModel(**job_data)
            db.add(job)

        db.commit()
        print(f"Successfully seeded {len(SEED_JOBS)} jobs!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
