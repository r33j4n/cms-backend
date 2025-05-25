from pydantic import BaseModel, Field
from typing import Optional, List

# Pydantic models for request validation

class FlatOwnerCreate(BaseModel):
    pin_no: str = Field(..., min_length=1, max_length=10)
    flat_no: str = Field(..., min_length=1, max_length=10)
    contact_no: str = Field(..., min_length=1, max_length=15)

class FlatOwnerResponse(BaseModel):
    id: int
    flat_no: str
    contact_no: str
    complaint_count: Optional[int] = None

class ComplaintCreate(BaseModel):
    pin_no: str = Field(..., min_length=1, max_length=10)
    flat_no: str = Field(..., min_length=1, max_length=10)
    complaint: str = Field(..., min_length=1)

class ComplaintResponse(BaseModel):
    id: int
    description: str
    domain: Optional[str] = None
    solution: Optional[str] = None
    is_checked: bool
    created_at: str
    proof_image: Optional[str] = None
    flat_no: Optional[str] = None
    contact_no: Optional[str] = None

class AdminLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class AdminLoginResponse(BaseModel):
    success: bool
    error: Optional[str] = None
