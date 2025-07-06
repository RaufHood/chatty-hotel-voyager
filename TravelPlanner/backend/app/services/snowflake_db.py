import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from typing import Optional, List, Dict, Any
from app.core.settings import settings
import pandas as pd

class SnowflakeDB:
    def __init__(self):
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Snowflake"""
        try:
            self.connection = snowflake.connector.connect(
                account=settings.snowflake_account,
                user=settings.snowflake_user,
                password=settings.snowflake_password,
                warehouse=settings.snowflake_warehouse,
                database=settings.snowflake_database,
                schema=settings.snowflake_schema,
                role=settings.snowflake_role
            )
        except Exception as e:
            print(f"Failed to connect to Snowflake: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all results
            results = cursor.fetchall()
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_insert(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute an INSERT query and return the number of affected rows"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error executing insert: {e}")
            self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute an UPDATE query and return the number of affected rows"""
        return self.execute_insert(query, params)
    
    def execute_delete(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute a DELETE query and return the number of affected rows"""
        return self.execute_insert(query, params)
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str) -> bool:
        """Insert a pandas DataFrame into a Snowflake table"""
        try:
            success, nchunks, nrows, _ = write_pandas(
                self.connection, 
                df, 
                table_name.upper(),
                auto_create_table=False
            )
            return success
        except Exception as e:
            print(f"Error inserting DataFrame: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = f"SELECT * FROM {settings.snowflake_users_table} WHERE EMAIL = %s"
        results = self.execute_query(query, {"email": email})
        return results[0] if results else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = f"SELECT * FROM {settings.snowflake_users_table} WHERE USER_ID = %s"
        results = self.execute_query(query, {"user_id": user_id})
        return results[0] if results else None
    
    def create_user(self, email: str, name: str, surname: str, auto_token: Optional[str] = None) -> int:
        """Create a new user and return the user_id"""
        query = f"""
        INSERT INTO {settings.snowflake_users_table} (EMAIL, NAME, SURNAME, AUTO_TOKEN)
        VALUES (%s, %s, %s, %s)
        """
        self.execute_insert(query, {
            "email": email,
            "name": name,
            "surname": surname,
            "auto_token": auto_token
        })
        
        # Get the created user_id
        user = self.get_user_by_email(email)
        return user["USER_ID"] if user else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user fields"""
        if not kwargs:
            return False
        
        set_clauses = []
        params = {"user_id": user_id}
        
        for key, value in kwargs.items():
            if value is not None:
                set_clauses.append(f"{key.upper()} = %s")
                params[key] = value
        
        if not set_clauses:
            return False
        
        query = f"UPDATE {settings.snowflake_users_table} SET {', '.join(set_clauses)} WHERE USER_ID = %s"
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()

# Global instance
snowflake_db = SnowflakeDB() 