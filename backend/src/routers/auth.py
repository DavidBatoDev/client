"""
Authentication router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database.connection import get_db_session
from ..schemas.auth_schemas import UserRegister, UserLogin, Token, PasswordChange
from ..schemas.user_schemas import UserResponse
from ..services.auth_service import auth_service
from ..models.users import User

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=Dict[str, Any])
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db_session)
):
    """
    Register a new user
    """
    result = await auth_service.register_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "message": "User registered successfully",
        "user": UserResponse.from_orm(result["user"]),
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.post("/login", response_model=Dict[str, Any])
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db_session)
):
    """
    Login user
    """
    result = await auth_service.login_user(
        db=db,
        email=user_data.email,
        password=user_data.password
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"]
        )
    
    return {
        "message": "Login successful",
        "user": UserResponse.from_orm(result["user"]),
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Get current user information
    """
    user = auth_service.get_current_user(db, credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return UserResponse.from_orm(user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Change user password
    """
    user = auth_service.get_current_user(db, credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    success = auth_service.change_password(
        db=db,
        user_id=user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password"
        )
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user (invalidate token)
    """
    # In a real implementation, you might want to maintain a blacklist of tokens
    # For now, we'll just return a success message
    return {"message": "Logged out successfully"}


@router.get("/verify-token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
):
    """
    Verify if token is valid
    """
    user = auth_service.get_current_user(db, credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {"valid": True, "user_id": user.id}


def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> User:
    """
    Dependency to get current user
    """
    user = auth_service.get_current_user(db, credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return user 