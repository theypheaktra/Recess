"""
User schemas - Pydantic models for API request/response
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserStatus


# Base schema with common fields
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    name_jp: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role_level: int = Field(..., ge=0, le=7)
    tier: int = Field(..., ge=0, le=2)
    org_id: Optional[int] = None


# For creating new user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


# For updating user
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_jp: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role_level: Optional[int] = Field(None, ge=0, le=7)
    tier: Optional[int] = Field(None, ge=0, le=2)
    org_id: Optional[int] = None
    status: Optional[UserStatus] = None


# For API response
class User(UserBase):
    id: int
    status: UserStatus
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# For authentication responses
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
