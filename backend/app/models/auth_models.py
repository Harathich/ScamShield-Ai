from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ScanHistoryResponse(BaseModel):
    id: int
    user_id: int
    input_type: str
    input_content: str
    overall_risk_score: int
    overall_threat_level: str
    agent_results: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
