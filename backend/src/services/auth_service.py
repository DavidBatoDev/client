"""
Authentication service for JWT handling and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from loguru import logger

from ..config.settings import get_settings
from ..models.users import User
from ..services.supabase_service import supabase_service

# Initialize settings
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Authentication service for handling user authentication and JWT tokens
    """
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a password
        """
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            return None
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email from database
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID from database
        """
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username from database
        """
        return db.query(User).filter(User.username == username).first()
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        """
        user = self.get_user_by_email(db, email)
        
        if not user:
            logger.warning(f"Authentication failed: User not found - {email}")
            return None
        
        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password - {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: User inactive - {email}")
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User authenticated successfully: {email}")
        return user
    
    def create_user(self, db: Session, email: str, username: str, password: str, full_name: str = None) -> User:
        """
        Create a new user
        """
        hashed_password = self.get_password_hash(password)
        
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created successfully: {email}")
        return user
    
    async def register_user(self, db: Session, email: str, username: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """
        Register a new user with Supabase integration
        """
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(db, email)
            if existing_user:
                return {
                    "success": False,
                    "error": "User already exists"
                }
            
            existing_username = self.get_user_by_username(db, username)
            if existing_username:
                return {
                    "success": False,
                    "error": "Username already taken"
                }
            
            # Create user in Supabase
            supabase_result = await supabase_service.sign_up(
                email=email,
                password=password,
                user_data={
                    "username": username,
                    "full_name": full_name
                }
            )
            
            if not supabase_result["success"]:
                return {
                    "success": False,
                    "error": supabase_result["error"]
                }
            
            # Create user in local database
            user = self.create_user(db, email, username, password, full_name)
            
            # Link Supabase user ID
            if supabase_result.get("user"):
                user.supabase_user_id = supabase_result["user"].id
                db.commit()
            
            # Create access token
            access_token = self.create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            return {
                "success": True,
                "user": user,
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def login_user(self, db: Session, email: str, password: str) -> Dict[str, Any]:
        """
        Login user with email and password
        """
        try:
            # Authenticate user
            user = self.authenticate_user(db, email, password)
            
            if not user:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
            
            # Create access token
            access_token = self.create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            return {
                "success": True,
                "user": user,
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """
        Get current user from JWT token
        """
        try:
            payload = self.verify_token(token)
            
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user = self.get_user_by_id(db, int(user_id))
            
            if not user or not user.is_active:
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    def update_user_profile(self, db: Session, user_id: int, profile_data: Dict[str, Any]) -> Optional[User]:
        """
        Update user profile
        """
        try:
            user = self.get_user_by_id(db, user_id)
            
            if not user:
                return None
            
            # Update allowed fields
            if "full_name" in profile_data:
                user.full_name = profile_data["full_name"]
            
            if "profile_image_url" in profile_data:
                user.profile_image_url = profile_data["profile_image_url"]
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User profile updated: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return None
    
    def change_password(self, db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user password
        """
        try:
            user = self.get_user_by_id(db, user_id)
            
            if not user:
                return False
            
            # Verify old password
            if not self.verify_password(old_password, user.hashed_password):
                return False
            
            # Update password
            user.hashed_password = self.get_password_hash(new_password)
            db.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False


# Global authentication service instance
auth_service = AuthService() 