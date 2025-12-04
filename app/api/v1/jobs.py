# jobs.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import date

# --- 1. Define the Pydantic Schema matching TypeScript Job interface ---
# This schema matches the Job interface from nextjs_govuk_experiment repository
class Job(BaseModel):
    """
    Job schema matching the TypeScript interface from nextjs_govuk_experiment.
    """
    id: str
    title: str
    description: str
    organisation: str
    location: str
    grade: str
    assignmentType: str
    personalSpec: str
    nationalityRequirement: Optional[str] = None
    summary: Optional[str] = None
    applyUrl: Optional[str] = None
    benefits: Optional[str] = None
    profession: Optional[str] = None
    applyDetail: Optional[str] = None
    salary: Optional[str] = None
    closingDate: Optional[str] = None
    jobNumbers: Optional[int] = None
    contacts: bool
    contactName: Optional[str] = None
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None
    recruitmentEmail: str

# --- 2. Define the Pydantic Schema for Job POST Data ---
# This class defines the structure for creating new jobs (without the auto-generated id)
class JobPost(BaseModel):
    """
    Schema for a new job post request (without id field).
    """
    title: str
    description: str
    organisation: str
    location: str
    grade: str
    assignmentType: str
    personalSpec: str
    nationalityRequirement: Optional[str] = None
    summary: Optional[str] = None
    applyUrl: Optional[str] = None
    benefits: Optional[str] = None
    profession: Optional[str] = None
    applyDetail: Optional[str] = None
    salary: Optional[str] = None
    closingDate: Optional[str] = None
    jobNumbers: Optional[int] = None
    contacts: bool = False
    contactName: Optional[str] = None
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None
    recruitmentEmail: str

# --- 3. Initialize Router and Mock Data ---

# Initialize the router for jobs-related endpoints
router = APIRouter()

# --- 4. Mock Data matching TypeScript interface ---

# Hardcoded job data matching the TypeScript Job interface
jobs_data = [
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
        "contacts": False,
        "recruitmentEmail": "recruitment@civilservice.gov.uk"
    },
    {
        "id": "9488",
        "title": "Police Service - Volunteer Curator",
        "description": "This is a fantastic job for a curator...",
        "organisation": "College of Policing",
        "location": "2 Horse Guards, Whitehall, London, SW1A 2AX",
        "grade": "Grade 6",
        "assignmentType": "Permanent",
        "personalSpec": "Some personal specification text",
        "closingDate": "20 December 2025",
        "contacts": False,
        "recruitmentEmail": "recruitment@civilservice.gov.uk"
    },
    {
        "id": "9487",
        "title": "Project Manager",
        "description": "This is a fantastic job for a project manager...",
        "organisation": "Home Office",
        "location": "2 Horse Guards, Whitehall, London, SW1A 2AX",
        "grade": "Senior Executive Office",
        "assignmentType": "Fixed Term Appointment (FTA)",
        "personalSpec": "Some personal specification text",
        "salary": "£39,000 to £46,200",
        "closingDate": "20 December 2025",
        "contacts": False,
        "recruitmentEmail": "recruitment@civilservice.gov.uk"
    },
    {
        "id": "9489",
        "title": "Dentist",
        "description": "This is a fantastic job for a dentist...",
        "organisation": "HM Revenue and Customs",
        "location": "Benton Park Road, Newcastle upon Tyne, NE7 7LX",
        "grade": "Higher Executive Office",
        "assignmentType": "Apprenticeship",
        "personalSpec": "Some personal specification text",
        "salary": "£99,000",
        "closingDate": "5 January 2026",
        "contacts": False,
        "recruitmentEmail": "recruitment@civilservice.gov.uk"
    }
]

# --- 5. GET all jobs endpoint ---

@router.get("/jobs", response_model=List[Job])
def get_all_jobs():
    """
    Returns the complete list of mock job data.
    """
    return jobs_data

# --- 6. POST endpoint to create a new job ---

@router.post("/jobs", response_model=Job, status_code=201)
def create_job(job: JobPost):
    """
    Accepts a new job post and adds it to the list of jobs.
    """
    # Generate a unique ID for the new job
    new_id = f"CSJ-{str(uuid.uuid4())[:8].upper()}"
    
    # Create the final job object with the generated ID
    new_job_dict = job.model_dump()
    new_job_dict["id"] = new_id
    new_job = Job(**new_job_dict)
    
    # Add the new job to our mock data list
    jobs_data.append(new_job.model_dump())
    
    # Return the created job object
    return new_job

# --- 7. GET single job by ID endpoint ---

@router.get("/jobs/{job_id}", response_model=Job)
def get_job_by_id(job_id: str):
    """
    Retrieves a single job based on its unique job ID.
    """
    # Loop through the list to find the job with the matching ID
    for job in jobs_data:
        if job["id"] == job_id:
            return job
    
    # If the loop finishes without finding a match, raise a 404 exception
    raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found")