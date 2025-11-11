# jobs.py

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import date

# --- 1. Define the Pydantic Schema for the Job POST Data ---
# This class defines the strict structure and data types for the incoming job data.
class JobPost(BaseModel):
    """
    Schema for a new job post request.
    """
    job_title: str
    department: str
    location: str
    salary: str # Using str for flexibility (e.g., "£40,000 - £50,000")
    grade: str
    closing_date: date # Use the date type for correct format validation
    summary: str
    responsibilities: str
    essential_criteria: str
    desirable_criteria: Optional[str] = None # Optional field

# --- 2. Define the Pydantic Schema for the Full Job Response ---
# This is what will be stored and returned. It includes the auto-generated fields.
class Job(JobPost):
    """
    Full job schema including system-generated fields.
    """
    job_id: str = Field(default_factory=lambda: f"CSJ-{str(uuid.uuid4())[:4].upper()}") # Auto-generate a job ID
    status: str = "Draft"
    views: int = 0

# --- 3. Initialize Router and Mock Data ---


# Initialize the router for jobs-related endpoints
router = APIRouter()

# --- 4. GET jobs (Existing) ---

# Hardcoded job data
jobs_data = [
    {"job_id": "CSJ-0001", "job_title": "Senior Product Manager", "status": "Advertised", "views": 234},
    {"job_id": "CSJ-0002", "job_title": "Performance Analyst", "status": "Draft", "views": 0},
    {"job_id": "CSJ-0003", "job_title": "Service Designer", "status": "Advertised", "views": 178},
    {"job_id": "CSJ-0004", "job_title": "Interaction Designer", "status": "Closed", "views": 421},
    {"job_id": "CSJ-0005", "job_title": "Delivery Manager", "status": "Draft", "views": 0},
    {"job_id": "CSJ-0006", "job_title": "Technical Architect", "status": "Closed", "views": 355},
    {"job_id": "CSJ-0007", "job_title": "Recruitment Lead", "status": "Advertised", "views": 292},
]

# Define the GET endpoint
@router.get("/jobs")
def get_all_jobs():
    """
    Returns the complete list of mock job data.
    """
    # FastAPI automatically converts the Python list to a JSON response
    return jobs_data

# --- 5. POST Endpoint (New) ---

@router.post("/jobs", response_model=Job, status_code=201)
def create_job(job: JobPost):
    """
    Accepts a new job post and adds it to the list of jobs.
    """
    # Create the final job object by spreading the JobPost data and adding defaults
    new_job = Job(**job.model_dump())
    
    # Add the new job to our mock data list
    jobs_data.append(new_job)
    
    # Return the created job object
    return new_job

# --- 6. get single job Endpoint ---
@router.get("/jobs/{job_id}", response_model=Job)
def get_job_by_id(job_id: str):
    """
    Retrieves a single job based on its unique job_id.
    """
    # Loop through the list to find the job with the matching ID
    for job in jobs_data:
        if job.job_id == job_id:
            return job
    
    # If the loop finishes without finding a match, raise a 404 exception
    raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found")