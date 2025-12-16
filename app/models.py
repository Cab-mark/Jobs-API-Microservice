"""SQLAlchemy models for the Jobs API."""

import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON

from app.database import Base

# Prefer JSONB on Postgres, but fall back to generic JSON for SQLite tests.
JSONType = JSONB().with_variant(JSON, "sqlite")


class JobModel(Base):
    """SQLAlchemy model for Job table."""

    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("external_id", name="uq_jobs_external_id"),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    version = Column(Integer, nullable=False, default=1)
    external_id = Column(String, nullable=False, index=True)
    approach = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    organisation = Column(String, nullable=False)
    location = Column(JSONType, nullable=False)
    grade = Column(String, nullable=False)
    assignment_type = Column(String, nullable=False)
    work_location = Column(JSONType, nullable=False)
    working_pattern = Column(JSONType, nullable=False)
    personal_spec = Column(Text, nullable=False)
    apply_detail = Column(Text, nullable=False)
    date_posted = Column(DateTime(timezone=True), nullable=False)
    closing_date = Column(DateTime(timezone=True), nullable=False)
    profession = Column(String, nullable=False)
    recruitment_email = Column(String, nullable=False)
    contacts = Column(JSONType, nullable=True)
    nationality_requirement = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    apply_url = Column(String, nullable=True)
    benefits = Column(Text, nullable=True)
    salary = Column(JSONType, nullable=True)
    job_numbers = Column(Integer, nullable=True)
    success_profile_details = Column(Text, nullable=True)
    diversity_statement = Column(Text, nullable=True)
    disability_confident = Column(Text, nullable=True)
    dc_status = Column(String, nullable=True)
    redeployment_scheme = Column(Text, nullable=True)
    prison_scheme = Column(Text, nullable=True)
    veteran_scheme = Column(Text, nullable=True)
    criminal_record_check = Column(Text, nullable=True)
    complaints_info = Column(Text, nullable=True)
    working_for_the_civil_service = Column(Text, nullable=True)
    eligibility_check = Column(Text, nullable=True)
    attachments = Column(JSONType, nullable=True)
