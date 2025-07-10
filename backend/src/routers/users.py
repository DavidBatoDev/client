"""
Users router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.connection import get_db_session
from ..schemas.user_schemas import UserResponse, UserUpdate, UserProfile
from ..services.auth_service import auth_service
from ..models.users import User
from .auth import get_current_user_dependency

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get current user profile
    """
    return UserProfile.from_orm(current_user)


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Update user profile
    """
    updated_user = auth_service.update_user_profile(
        db=db,
        user_id=current_user.id,
        profile_data=profile_data.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    return UserProfile.from_orm(updated_user)


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    Get user by ID (public profile)
    """
    user = auth_service.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile.from_orm(user)


@router.get("/", response_model=List[UserProfile])
async def list_users(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db_session)
):
    """
    List users (for admin or discovery)
    """
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    return [UserProfile.from_orm(user) for user in users] 