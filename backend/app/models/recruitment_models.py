from typing import List, Optional
from pydantic import BaseModel, Field

class JobInformation(BaseModel):
    job_title: Optional[str] = None
    company_claim: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    job_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    employment_type: Optional[str] = None
    compensation: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)
    application_method: Optional[str] = None
    contact_method: Optional[str] = None
    interview_process: Optional[str] = None
    recruiter_instructions: Optional[str] = None

class ConsistencyFinding(BaseModel):
    category: str
    finding: str
    evidence: str

class RecruitmentResponse(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    confidence: float = Field(ge=0.0, le=1.0)
    job_information: JobInformation
    consistency_findings: List[ConsistencyFinding] = Field(default_factory=list)
    recruitment_red_flags: List[str] = Field(default_factory=list)
    reason: str
    recommendations: List[str] = Field(default_factory=list)

class RecruitmentRequest(BaseModel):
    text: str
