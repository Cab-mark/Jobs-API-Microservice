import os
from datetime import datetime, timedelta, timezone
import pathlib
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test_jobs.db"
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
import pytest

from app.database import Base, engine, get_db, SessionLocal
from app.main import app
from app.api.v1.jobs import JobCreatePayload
from jobs_data_contracts.jobs import models as dc_models


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def build_job_payload(external_id: str = "ext-1") -> dict:
    location = dc_models.FixedLocations.model_validate(
        {"townName": "London", "region": "London", "latitude": 51.5, "longitude": -0.1}
    )

    payload = {
        "externalId": external_id,
        "approach": dc_models.Approach.external.value,
        "title": "Backend Engineer",
        "description": "Build APIs",
        "organisation": "Cabinet Office",
        "location": [location.model_dump(mode="json", by_alias=True)],
        "grade": dc_models.Grade.grade_7.value,
        "assignmentType": dc_models.Assignments.permanent.value,
        "workLocation": [dc_models.WorkLocation.office_based.value],
        "workingPattern": [dc_models.WorkingPattern.full_time.value],
        "personalSpec": "Experienced engineer",
        "applyDetail": "Send CV",
        "dateClosing": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "datePosted": datetime.now(timezone.utc).isoformat(),
        "profession": dc_models.Profession.policy.value,
        "recruitmentEmail": "jobs@example.com",
    }
    validated = JobCreatePayload.model_validate(payload)
    return validated.model_dump(by_alias=True, mode="json")


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_job_and_get_summary_and_detail():
    payload = build_job_payload()
    response = client.post("/jobs", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert response.headers["Location"] == "/jobs/ext-1"
    assert data["externalId"] == "ext-1"
    assert data["title"] == payload["title"]
    assert data["approach"] == payload["approach"]
    assert data["version"] == 1
    assert "id" in data

    list_response = client.get("/jobs")
    assert list_response.status_code == 200
    summaries = list_response.json()
    assert len(summaries) == 1
    assert summaries[0]["externalId"] == "ext-1"
    assert summaries[0]["title"] == payload["title"]
    assert summaries[0]["version"] == 1

    detail_response = client.get("/jobs/ext-1")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["externalId"] == "ext-1"
    assert detail["dateClosing"].startswith(payload["dateClosing"][:10])
    assert detail["datePosted"].startswith(payload["datePosted"][:10])
    assert detail["version"] == 1


def test_put_requires_matching_external_id():
    payload = build_job_payload()
    create = client.post("/jobs", json=payload)
    assert create.status_code == 201

    replace_payload = build_job_payload(external_id="other-id")
    replace = client.put("/jobs/ext-1", json=replace_payload)
    assert replace.status_code == 400


def test_patch_rejects_external_id_and_updates_fields():
    payload = build_job_payload()
    client.post("/jobs", json=payload)

    future_date = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
    patch_payload = {"externalId": "new-id", "dateClosing": future_date}
    bad_patch = client.patch("/jobs/ext-1", json=patch_payload)
    assert bad_patch.status_code == 400

    patch_payload = {"dateClosing": future_date, "summary": "Updated"}
    ok_patch = client.patch("/jobs/ext-1", json=patch_payload)
    assert ok_patch.status_code == 200
    patched = ok_patch.json()
    assert patched["dateClosing"].startswith(future_date[:10])
    assert patched["summary"] == "Updated"
    assert patched["version"] == 2


def test_put_increments_version():
    payload = build_job_payload()
    create = client.post("/jobs", json=payload)
    assert create.status_code == 201
    original = create.json()
    assert original["version"] == 1

    replacement = build_job_payload()
    replacement["title"] = "Backend Engineer Updated"
    replace = client.put("/jobs/ext-1", json=replacement)
    assert replace.status_code == 200
    replaced = replace.json()
    assert replaced["title"] == "Backend Engineer Updated"
    assert replaced["version"] == 2
