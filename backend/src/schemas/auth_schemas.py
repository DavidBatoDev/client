"""
Authentication Pydantic schemas
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional


class UserRegister(BaseModel):
    """
    Schema for user registration
    """
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    """
    Schema for user login
    """
    email: EmailStr
    password: str


class Token(BaseModel):
    """
    Schema for token response
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for token data
    """
    email: Optional[str] = None
    user_id: Optional[int] = None


class PasswordChange(BaseModel):
    """
    Schema for password change
    """
    old_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v


class PasswordReset(BaseModel):
    """
    Schema for password reset request
    """
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """
    Schema for password reset confirmation
    """
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v 