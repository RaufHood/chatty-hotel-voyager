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
user_service = UserService() 