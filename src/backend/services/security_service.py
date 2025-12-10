import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional
# from bson import ObjectId

class AuthService:
    """Service for user authentication and management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return AuthService.hash_password(plain_password) == hashed_password

auth_service = AuthService()