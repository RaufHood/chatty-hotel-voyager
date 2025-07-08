<<<<<<< Updated upstream
from typing import Optional, Dict, Any
from app.services.snowflake_db import snowflake_db
from app.schemas.auth import OAuthProvider
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.jwt_service import create_access_token
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.db = snowflake_db
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from Snowflake"""
        try:
            return self.db.get_user_by_email(email)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID from Snowflake"""
        try:
            return self.db.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    def create_user_from_oauth(self, user_data: UserCreate) -> Optional[Dict[str, Any]]:
        """Create a new user from OAuth data"""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(user_data.email)
            if existing_user:
                logger.info(f"User {user_data.email} already exists")
                return existing_user
            
            # Create new user
            user_id = self.db.create_user(
                email=user_data.email,
                name=user_data.name,
                surname=user_data.surname,
                auto_token=None  # Will be set after JWT creation
            )
            
            if user_id:
                # Generate JWT token for auto_token
                access_token = create_access_token(
                    data={"sub": user_data.email, "user_id": user_id}
                )
                
                # Update user with auto_token
                self.db.update_user(user_id, auto_token=access_token)
                
                # Return the created user
                return self.get_user_by_id(user_id)
            
            return None
        except Exception as e:
            logger.error(f"Error creating user from OAuth: {e}")
            return None
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> bool:
        """Update user information"""
        try:
            update_data = {}
            if user_update.email is not None:
                update_data["email"] = user_update.email
            if user_update.name is not None:
                update_data["name"] = user_update.name
            if user_update.surname is not None:
                update_data["surname"] = user_update.surname
            if user_update.auto_token is not None:
                update_data["auto_token"] = user_update.auto_token
            
            return self.db.update_user(user_id, **update_data)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    def get_or_create_user(self, oauth_data: Dict[str, Any], provider: OAuthProvider) -> Optional[Dict[str, Any]]:
        """Get existing user or create new one from OAuth data"""
        try:
            email = oauth_data.get("email")
            if not email:
                logger.error("No email found in OAuth data")
                return None
            
            # Try to get existing user
            user = self.get_user_by_email(email)
            if user:
                logger.info(f"Found existing user: {email}")
                return user
            
            # Create new user
            name = oauth_data.get("given_name", oauth_data.get("name", ""))
            surname = oauth_data.get("family_name", "")
            
            user_create = UserCreate(
                email=email,
                name=name,
                surname=surname,
                oauth_provider=provider,
                oauth_id=oauth_data.get("sub", oauth_data.get("id", ""))
            )
            
            return self.create_user_from_oauth(user_create)
        except Exception as e:
            logger.error(f"Error in get_or_create_user: {e}")
            return None
    
    def convert_to_response(self, user_data: Dict[str, Any]) -> UserResponse:
        """Convert database user data to UserResponse schema"""
        return UserResponse(
            user_id=user_data["USER_ID"],
            email=user_data["EMAIL"],
            name=user_data["NAME"],
            surname=user_data["SURNAME"],
            auto_token=user_data.get("AUTO_TOKEN"),
            oauth_provider=None,  # Not stored in Snowflake schema
            oauth_id=None,  # Not stored in Snowflake schema
            is_active=True,  # Not stored in Snowflake schema
            created_at=None,  # Not stored in Snowflake schema
            updated_at=None  # Not stored in Snowflake schema
        )

# Global instance
=======
from typing import Optional, Dict, Any
from app.services.database import get_database
from app.schemas.user import UserCreate, UserUpdate, UserResponse
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.db = None  # Will be initialized when needed
    
    def _get_db(self):
        """Get database instance"""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from Snowflake"""
        try:
            db = self._get_db()
            return db.get_user_by_email(email)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID from Snowflake"""
        try:
            db = self._get_db()
            return db.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    

    
    def update_user(self, user_id: int, user_update: UserUpdate) -> bool:
        """Update user information"""
        try:
            db = self._get_db()
            update_data = {}
            if user_update.email is not None:
                update_data["email"] = user_update.email
            if user_update.name is not None:
                update_data["name"] = user_update.name
            if user_update.surname is not None:
                update_data["surname"] = user_update.surname
            
            return db.update_user(user_id, **update_data)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    

    
    def convert_to_response(self, user_data: Dict[str, Any]) -> UserResponse:
        """Convert database user data to UserResponse schema"""
        return UserResponse(
            user_id=user_data["USER_ID"],
            email=user_data["EMAIL"],
            name=user_data["NAME"],
            surname=user_data["SURNAME"],
            is_active=True,  # Not stored in Snowflake schema
            created_at=None,  # Not stored in Snowflake schema
            updated_at=None  # Not stored in Snowflake schema
        )

# Global instance
>>>>>>> Stashed changes
user_service = UserService() 