from datetime import datetime, timezone
from enum import Enum
from typing import List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import ConfigDict, Field
from sqlalchemy.orm import Session

from jobs_data_contracts.jobs import models as dc_models

from app.database import get_db
from app.models import JobModel


class JobCreatePayload(dc_models.JobCreate):
    """Extend jobs-data-contracts JobCreate to include datePosted per OpenAPI."""

    date_posted: dc_models.AwareDatetime = Field(..., alias="datePosted")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class JobUpdatePayload(dc_models.JobUpdate):
    """Patch payload including optional datePosted."""

    date_posted: dc_models.AwareDatetime | None = Field(None, alias="datePosted")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class JobResponse(dc_models.Job):
    """Job response including datePosted."""

    date_posted: dc_models.AwareDatetime = Field(..., alias="datePosted")
    version: int
    model_config = ConfigDict(populate_by_name=True)


class JobSummaryResponse(dc_models.JobSummary):
    """Job summary response including version."""

    version: int
    model_config = ConfigDict(populate_by_name=True)


router = APIRouter()

FIELD_MAP = {
    "externalId": "external_id",
    "assignmentType": "assignment_type",
    "workLocation": "work_location",
    "workingPattern": "working_pattern",
    "personalSpec": "personal_spec",
    "applyDetail": "apply_detail",
    "closingDate": "closing_date",
    "recruitmentEmail": "recruitment_email",
    "nationalityRequirement": "nationality_requirement",
    "jobNumbers": "job_numbers",
    "successProfileDetails": "success_profile_details",
    "diversityStatement": "diversity_statement",
    "disabilityConfident": "disability_confident",
    "applyUrl": "apply_url",
    "dcStatus": "dc_status",
    "redeploymentScheme": "redeployment_scheme",
    "prisonScheme": "prison_scheme",
    "veteranScheme": "veteran_scheme",
    "criminalRecordCheck": "criminal_record_check",
    "complaintsInfo": "complaints_info",
    "workingForTheCivilService": "working_for_the_civil_service",
    "eligibilityCheck": "eligibility_check",
    "dateClosing": "closing_date",
    "datePosted": "date_posted",
}


def _to_plain(value: Any) -> Any:
    """Convert pydantic/enums into JSON/DB-friendly structures."""
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True)
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    if isinstance(value, dict):
        return {k: _to_plain(v) for k, v in value.items()}
    if isinstance(value, datetime):
        return value
    return str(value) if not isinstance(value, (str, int, float, bool)) else value


def _normalize_payload(payload: dc_models.BaseModel, *, exclude_unset: bool = False) -> Dict[str, Any]:
    raw = payload.model_dump(by_alias=True, exclude_unset=exclude_unset)
    normalized: Dict[str, Any] = {}
    for key, value in raw.items():
        column = FIELD_MAP.get(key, key)
        normalized[column] = _to_plain(value)
    return normalized


def _ensure_tz(value: datetime | None) -> datetime | None:
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _job_model_to_response(job_model: JobModel) -> JobResponse:
    payload = {
        "id": job_model.id,
        "version": job_model.version,
        "external_id": job_model.external_id,
        "approach": job_model.approach,
        "title": job_model.title,
        "description": job_model.description,
        "organisation": job_model.organisation,
        "location": job_model.location,
        "grade": job_model.grade,
        "assignment_type": job_model.assignment_type,
        "work_location": job_model.work_location,
        "working_pattern": job_model.working_pattern,
        "personal_spec": job_model.personal_spec,
        "apply_detail": job_model.apply_detail,
        "date_posted": _ensure_tz(job_model.date_posted),
        "date_closing": _ensure_tz(job_model.closing_date),
        "profession": job_model.profession,
        "recruitment_email": job_model.recruitment_email,
        "contacts": job_model.contacts,
        "nationality_requirement": job_model.nationality_requirement,
        "summary": job_model.summary,
        "apply_url": job_model.apply_url,
        "benefits": job_model.benefits,
        "salary": job_model.salary,
        "job_numbers": job_model.job_numbers,
        "success_profile_details": job_model.success_profile_details,
        "diversity_statement": job_model.diversity_statement,
        "disability_confident": job_model.disability_confident,
        "dc_status": job_model.dc_status,
        "redeployment_scheme": job_model.redeployment_scheme,
        "prison_scheme": job_model.prison_scheme,
        "veteran_scheme": job_model.veteran_scheme,
        "criminal_record_check": job_model.criminal_record_check,
        "complaints_info": job_model.complaints_info,
        "working_for_the_civil_service": job_model.working_for_the_civil_service,
        "eligibility_check": job_model.eligibility_check,
        "attachments": job_model.attachments,
    }
    return JobResponse.model_validate(payload)


@router.get("/jobs", response_model=List[JobSummaryResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobModel).all()
    summaries = []
    for job in jobs:
        summary = {
            "id": job.id,
            "version": job.version,
            "externalId": job.external_id,
            "title": job.title,
            "approach": job.approach,
            "dateClosing": _ensure_tz(job.closing_date),
        }
        summaries.append(JobSummaryResponse.model_validate(summary))
    return summaries


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_payload: JobCreatePayload, response: Response, db: Session = Depends(get_db)):
    existing = db.query(JobModel).filter(JobModel.external_id == job_payload.external_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job with externalId already exists")

    normalized = _normalize_payload(job_payload)
    new_job = JobModel(**normalized)

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    response.headers["Location"] = f"/jobs/{new_job.external_id}"
    return _job_model_to_response(new_job)


@router.get("/jobs/{external_id}", response_model=JobResponse)
def get_job_by_external_id(external_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.external_id == external_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with externalId '{external_id}' not found")
    return _job_model_to_response(job)


@router.put("/jobs/{external_id}", response_model=JobResponse)
def replace_job(external_id: str, job_payload: JobCreatePayload, db: Session = Depends(get_db)):
    if job_payload.external_id != external_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="externalId in body must match path parameter",
        )

    job = db.query(JobModel).filter(JobModel.external_id == external_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with externalId '{external_id}' not found")

    normalized = _normalize_payload(job_payload)
    for key, value in normalized.items():
        if key == "id":
            continue
        setattr(job, key, value)

    job.version = (job.version or 0) + 1
    db.commit()
    db.refresh(job)
    return _job_model_to_response(job)


@router.patch("/jobs/{external_id}", response_model=JobResponse)
def update_job(
    external_id: str,
    job_payload: JobUpdatePayload,
    db: Session = Depends(get_db),
):
    job = db.query(JobModel).filter(JobModel.external_id == external_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with externalId '{external_id}' not found")

    updates = _normalize_payload(job_payload, exclude_unset=True)
    if "external_id" in updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="externalId cannot be modified via PATCH",
        )
    if updates:
        for key, value in updates.items():
            if key == "id":
                continue
            setattr(job, key, value)
        job.version = (job.version or 0) + 1
        db.commit()
        db.refresh(job)

    return _job_model_to_response(job)
