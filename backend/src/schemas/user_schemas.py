"""
User Pydantic schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base user schema
    """
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False


class UserCreate(UserBase):
    """
    Schema for creating a user
    """
    password: str


class UserUpdate(BaseModel):
    """
    Schema for updating a user
    """
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserResponse(UserBase):
    """
    Schema for user response
    """
    id: int
    profile_image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """
    Schema for user profile
    """
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True 