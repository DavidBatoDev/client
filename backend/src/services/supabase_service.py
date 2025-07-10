"""
Supabase service for authentication and storage
"""

from supabase import create_client, Client
from typing import Dict, Any, Optional, List
from loguru import logger
import asyncio
from datetime import datetime
import os

from ..config.settings import get_settings

# Initialize settings
settings = get_settings()


class SupabaseService:
    """
    Supabase service for handling authentication and storage operations
    """
    
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.admin_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    # Authentication methods
    
    async def sign_up(self, email: str, password: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Sign up a new user
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            
            if response.user:
                logger.info(f"User signed up successfully: {email}")
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session
                }
            else:
                logger.error(f"Sign up failed for email: {email}")
                return {
                    "success": False,
                    "error": "Sign up failed"
                }
                
        except Exception as e:
            logger.error(f"Error signing up user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in a user
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                logger.info(f"User signed in successfully: {email}")
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session
                }
            else:
                logger.error(f"Sign in failed for email: {email}")
                return {
                    "success": False,
                    "error": "Sign in failed"
                }
                
        except Exception as e:
            logger.error(f"Error signing in user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """
        Sign out a user
        """
        try:
            self.client.auth.set_session(access_token, None)
            response = self.client.auth.sign_out()
            
            logger.info("User signed out successfully")
            return {
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error signing out user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from access token
        """
        try:
            self.client.auth.set_session(access_token, None)
            response = self.client.auth.get_user()
            
            if response.user:
                return {
                    "success": True,
                    "user": response.user
                }
            else:
                return {
                    "success": False,
                    "error": "User not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user access token
        """
        try:
            response = self.client.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "success": True,
                    "session": response.session
                }
            else:
                return {
                    "success": False,
                    "error": "Token refresh failed"
                }
                
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Storage methods
    
    async def upload_image(self, file_path: str, file_content: bytes, bucket: str = "images") -> Dict[str, Any]:
        """
        Upload image to Supabase storage
        """
        try:
            response = self.client.storage.from_(bucket).upload(
                file_path,
                file_content,
                {
                    "content-type": "image/*",
                    "upsert": True
                }
            )
            
            if response.path:
                # Get public URL
                public_url = self.client.storage.from_(bucket).get_public_url(file_path)
                
                logger.info(f"Image uploaded successfully: {file_path}")
                return {
                    "success": True,
                    "path": response.path,
                    "public_url": public_url
                }
            else:
                logger.error(f"Image upload failed: {file_path}")
                return {
                    "success": False,
                    "error": "Upload failed"
                }
                
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_image(self, file_path: str, bucket: str = "images") -> Dict[str, Any]:
        """
        Delete image from Supabase storage
        """
        try:
            response = self.client.storage.from_(bucket).remove([file_path])
            
            if response:
                logger.info(f"Image deleted successfully: {file_path}")
                return {
                    "success": True
                }
            else:
                logger.error(f"Image deletion failed: {file_path}")
                return {
                    "success": False,
                    "error": "Deletion failed"
                }
                
        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_image_public_url(self, file_path: str, bucket: str = "images") -> str:
        """
        Get public URL for an image
        """
        try:
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            return public_url
        except Exception as e:
            logger.error(f"Error getting public URL: {e}")
            return ""
    
    async def list_images(self, folder: str = "", bucket: str = "images") -> List[Dict[str, Any]]:
        """
        List images in a folder
        """
        try:
            response = self.client.storage.from_(bucket).list(folder)
            
            if response:
                return [
                    {
                        "name": item["name"],
                        "size": item["metadata"]["size"],
                        "created_at": item["created_at"],
                        "updated_at": item["updated_at"]
                    }
                    for item in response
                ]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error listing images: {e}")
            return []
    
    # Database methods using Supabase client
    
    async def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create user profile in Supabase
        """
        try:
            response = self.admin_client.table("users").insert({
                "supabase_user_id": user_id,
                **profile_data
            }).execute()
            
            if response.data:
                logger.info(f"User profile created: {user_id}")
                return {
                    "success": True,
                    "data": response.data[0]
                }
            else:
                logger.error(f"User profile creation failed: {user_id}")
                return {
                    "success": False,
                    "error": "Profile creation failed"
                }
                
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile from Supabase
        """
        try:
            response = self.admin_client.table("users").select("*").eq("supabase_user_id", user_id).execute()
            
            if response.data:
                return {
                    "success": True,
                    "data": response.data[0]
                }
            else:
                return {
                    "success": False,
                    "error": "Profile not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global Supabase service instance
supabase_service = SupabaseService() 