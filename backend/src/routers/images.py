"""
Images router
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from datetime import datetime

from ..database.connection import get_db_session
from ..schemas.image_schemas import ImageResponse, ImageUpload, ImageUpdate
from ..models.users import User
from ..models.images import Image
from ..services.supabase_service import supabase_service
from ..config.settings import get_settings
from .auth import get_current_user_dependency

router = APIRouter()
settings = get_settings()


@router.post("/upload", response_model=ImageUpload)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Upload a new image
    """
    # Validate file type
    if file.content_type not in settings.allowed_file_types_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Upload to Supabase Storage
        storage_path = f"users/{current_user.id}/images/{unique_filename}"
        upload_result = await supabase_service.upload_image(
            file_path=storage_path,
            file_content=file_content
        )
        
        if not upload_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image to storage"
            )
        
        # Create image record in database
        image = Image(
            user_id=current_user.id,
            original_filename=file.filename,
            filename=unique_filename,
            file_path=storage_path,
            file_size=len(file_content),
            content_type=file.content_type,
            supabase_storage_path=upload_result["path"],
            public_url=upload_result["public_url"]
        )
        
        db.add(image)
        db.commit()
        db.refresh(image)
        
        return ImageUpload.from_orm(image)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )


@router.get("/", response_model=List[ImageResponse])
async def list_images(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    List user's images
    """
    images = db.query(Image).filter(
        Image.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [ImageResponse.from_orm(image) for image in images]


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Get specific image by ID
    """
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return ImageResponse.from_orm(image)


@router.put("/{image_id}", response_model=ImageResponse)
async def update_image(
    image_id: int,
    image_data: ImageUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Update image metadata
    """
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Update fields
    for field, value in image_data.dict(exclude_unset=True).items():
        setattr(image, field, value)
    
    db.commit()
    db.refresh(image)
    
    return ImageResponse.from_orm(image)


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Delete an image
    """
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    try:
        # Delete from Supabase Storage
        if image.supabase_storage_path:
            await supabase_service.delete_image(image.supabase_storage_path)
        
        # Delete from database
        db.delete(image)
        db.commit()
        
        return {"message": "Image deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image: {str(e)}"
        ) 