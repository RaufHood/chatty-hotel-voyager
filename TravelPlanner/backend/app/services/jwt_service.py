import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.settings import settings
from app.models.user import User as UserModel
from app.schemas.auth import Token, User
from app.schemas.user import UserResponse

class JWTService:
    """Centralized JWT service for consistent token handling across all auth methods"""
    
    @staticmethod
    def create_token(user: UserModel) -> Token:
        """
        Create a standardized JWT token for any authenticated user
        
        Args:
            user: User model instance
            
        Returns:
            Token: Standardized token response
        """
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)
        expire = datetime.utcnow() + expires_delta
        
        # Standardized payload structure for all auth methods
        payload = {
            "sub": str(user.id),  # Subject (user ID)
            "email": user.email,
            "oauth_provider": user.oauth_provider.value if user.oauth_provider else None,
            "oauth_id": user.oauth_id,
            "iat": datetime.utcnow(),  # Issued at
            "exp": expire,  # Expiration
            "type": "access"  # Token type
        }
        
        # Encode JWT with consistent algorithm and secret
        encoded_jwt = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        # Create refresh token
        refresh_token = JWTService.create_refresh_token(user)
        
        # Return standardized token response with refresh token
        return Token(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_in=settings.jwt_expire_minutes * 60,
            refresh_token=refresh_token,
            user=User.from_orm(user)
        )
    
    @staticmethod
    def create_token_from_data(user_data: Dict[str, Any]) -> Token:
        """
        Create a standardized JWT token from Snowflake user data
        
        Args:
            user_data: Dictionary containing user data from Snowflake
            
        Returns:
            Token: Standardized token response
        """
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)
        expire = datetime.utcnow() + expires_delta
        
        # Standardized payload structure for all auth methods
        payload = {
            "sub": str(user_data["USER_ID"]),  # Subject (user ID)
            "email": user_data["EMAIL"],
            "iat": datetime.utcnow(),  # Issued at
            "exp": expire,  # Expiration
            "type": "access"  # Token type
        }
        
        # Encode JWT with consistent algorithm and secret
        encoded_jwt = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        # Create refresh token
        refresh_token = JWTService.create_refresh_token_from_data(user_data)
        
        # Create user response object
        user_response = UserResponse(
            user_id=user_data["USER_ID"],
            email=user_data["EMAIL"],
            name=user_data["NAME"],
            surname=user_data["SURNAME"],
            auto_token=user_data.get("AUTO_TOKEN"),
            oauth_provider=None,
            oauth_id=None,
            is_active=True,
            created_at=None,
            updated_at=None
        )
        
        # Return standardized token response with refresh token
        return Token(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_in=settings.jwt_expire_minutes * 60,
            refresh_token=refresh_token,
            user=user_response
        )
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return standardized payload
        
        Args:
            token: JWT token string
            
        Returns:
            Optional[Dict]: Token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            # Validate required fields
            required_fields = ["sub", "email", "exp", "type"]
            if not all(field in payload for field in required_fields):
                return None
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                return None
            
            return payload
            
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def create_refresh_token(user: UserModel) -> str:
        """
        Create a refresh token for token renewal
        
        Args:
            user: User model instance
            
        Returns:
            str: Refresh token
        """
        expires_delta = timedelta(days=7)  # Refresh tokens last longer
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "iat": datetime.utcnow(),
            "exp": expire,
            "type": "refresh"
        }
        
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
    
    @staticmethod
    def create_refresh_token_from_data(user_data: Dict[str, Any]) -> str:
        """
        Create a refresh token from Snowflake user data
        
        Args:
            user_data: Dictionary containing user data from Snowflake
            
        Returns:
            str: Refresh token
        """
        expires_delta = timedelta(days=7)  # Refresh tokens last longer
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": str(user_data["USER_ID"]),
            "email": user_data["EMAIL"],
            "iat": datetime.utcnow(),
            "exp": expire,
            "type": "refresh"
        }
        
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
    
    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify refresh token
        
        Args:
            token: Refresh token string
            
        Returns:
            Optional[Dict]: Token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            # Check if it's a refresh token
            if payload.get("type") != "refresh":
                return None
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                return None
            
            return payload
            
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def extract_user_id_from_token(token: str) -> Optional[int]:
        """
        Extract user ID from token for quick verification
        
        Args:
            token: JWT token string
            
        Returns:
            Optional[int]: User ID if token is valid, None otherwise
        """
        payload = JWTService.verify_token(token)
        if payload and "sub" in payload:
            try:
                return int(payload["sub"])
            except (ValueError, TypeError):
                return None
        return None

# Global JWT service instance
jwt_service = JWTService() 