"""
Image Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ImageBase(BaseModel):
    """
    Base image schema
    """
    original_filename: str
    content_type: str
    width: Optional[int] = None
    height: Optional[int] = None


class ImageCreate(ImageBase):
    """
    Schema for creating an image
    """
    file_size: int
    filename: str
    file_path: str


class ImageUpdate(BaseModel):
    """
    Schema for updating an image
    """
    processing_status: Optional[str] = None
    processing_error: Optional[str] = None
    is_processed: Optional[bool] = None
    width: Optional[int] = None
    height: Optional[int] = None


class ImageResponse(ImageBase):
    """
    Schema for image response
    """
    id: int
    user_id: int
    filename: str
    file_size: int
    format: Optional[str] = None
    public_url: Optional[str] = None
    is_processed: bool
    processing_status: str
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ImageUpload(BaseModel):
    """
    Schema for image upload response
    """
    id: int
    filename: str
    public_url: Optional[str] = None
    file_size: int
    content_type: str
    
    class Config:
        from_attributes = True 