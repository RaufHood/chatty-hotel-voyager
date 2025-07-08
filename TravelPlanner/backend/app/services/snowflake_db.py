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
    
    # Trip-related functions
    def list_trips(self, user_id: int) -> List[Dict[str, Any]]:
        """List all trips for a specific user"""
        query = f"""
        SELECT 
            TRIP_ID,
            USER_ID,
            DATE_START,
            DATE_END
        FROM {settings.snowflake_trips_table} 
        WHERE USER_ID = %s
        ORDER BY DATE_START DESC
        """
        return self.execute_query(query, {"user_id": user_id})
    
    def get_trip_by_id(self, trip_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific trip by trip_id"""
        query = f"""
        SELECT 
            TRIP_ID,
            USER_ID,
            DATE_START,
            DATE_END
        FROM {settings.snowflake_trips_table} 
        WHERE TRIP_ID = %s
        """
        results = self.execute_query(query, {"trip_id": trip_id})
        return results[0] if results else None
    
    def get_trip_legs(self, trip_id: int) -> List[Dict[str, Any]]:
        """Get all trip legs for a specific trip"""
        query = f"""
        SELECT 
            TL.TRIP_LEG_ID,
            TL.TRIP_ID,
            TL.USER_ID,
            TL.HOTEL_ID,
            TL.ARRIVAL_DATE,
            TL.DEPARTURE_DATE,
            TL.STAY_PRICE,
            H.HOTEL_NAME,
            H.STARS,
            H.RATING,
            H.LATITUDE,
            H.LONGITUDE,
            H.COUNTRY_CODE,
            H.CITY_CODE,
            H.HOTEL_TYPE
        FROM {settings.snowflake_trip_legs_table} TL
        LEFT JOIN {settings.snowflake_hotels_table} H ON TL.HOTEL_ID = H.HOTEL_ID
        WHERE TL.TRIP_ID = %s
        ORDER BY TL.ARRIVAL_DATE
        """
        return self.execute_query(query, {"trip_id": trip_id})
    
    def get_hotels_in_trip(self, trip_id: int) -> List[Dict[str, Any]]:
        """Get all hotels booked in a specific trip"""
        query = f"""
        SELECT DISTINCT
            H.HOTEL_ID,
            H.HOTEL_NAME,
            H.STARS,
            H.RATING,
            H.LATITUDE,
            H.LONGITUDE,
            H.COUNTRY_CODE,
            H.CITY_CODE,
            H.HOTEL_TYPE,
            TL.ARRIVAL_DATE,
            TL.DEPARTURE_DATE,
            TL.STAY_PRICE
        FROM {settings.snowflake_trip_legs_table} TL
        INNER JOIN {settings.snowflake_hotels_table} H ON TL.HOTEL_ID = H.HOTEL_ID
        WHERE TL.TRIP_ID = %s
        ORDER BY TL.ARRIVAL_DATE
        """
        return self.execute_query(query, {"trip_id": trip_id})
    
    def create_trip(self, user_id: int, date_start: str, date_end: str) -> int:
        """Create a new trip and return the trip_id"""
        query = f"""
        INSERT INTO {settings.snowflake_trips_table} (USER_ID, DATE_START, DATE_END)
        VALUES (%s, %s, %s)
        """
        self.execute_insert(query, {
            "user_id": user_id,
            "date_start": date_start,
            "date_end": date_end
        })
        
        # Get the created trip_id by finding the most recent trip for this user
        query_get_id = f"""
        SELECT TRIP_ID 
        FROM {settings.snowflake_trips_table} 
        WHERE USER_ID = %s 
        ORDER BY TRIP_ID DESC 
        LIMIT 1
        """
        results = self.execute_query(query_get_id, {"user_id": user_id})
        return results[0]["TRIP_ID"] if results else None
    
    def add_trip_leg(self, trip_id: int, user_id: int, hotel_id: int, 
                     arrival_date: str, departure_date: str, stay_price: float) -> int:
        """Add a trip leg to a trip and return the trip_leg_id"""
        query = f"""
        INSERT INTO {settings.snowflake_trip_legs_table} 
        (TRIP_ID, USER_ID, HOTEL_ID, ARRIVAL_DATE, DEPARTURE_DATE, STAY_PRICE)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.execute_insert(query, {
            "trip_id": trip_id,
            "user_id": user_id,
            "hotel_id": hotel_id,
            "arrival_date": arrival_date,
            "departure_date": departure_date,
            "stay_price": stay_price
        })
        
        # Get the created trip_leg_id
        query_get_id = f"""
        SELECT TRIP_LEG_ID 
        FROM {settings.snowflake_trip_legs_table} 
        WHERE TRIP_ID = %s AND HOTEL_ID = %s AND ARRIVAL_DATE = %s
        ORDER BY TRIP_LEG_ID DESC 
        LIMIT 1
        """
        results = self.execute_query(query_get_id, {
            "trip_id": trip_id,
            "hotel_id": hotel_id,
            "arrival_date": arrival_date
        })
        return results[0]["TRIP_LEG_ID"] if results else None
    
    def get_hotel_by_id(self, hotel_id: int) -> Optional[Dict[str, Any]]:
        """Get a single hotel by hotel_id"""
        query = f"SELECT * FROM {settings.snowflake_hotels_table} WHERE HOTEL_ID = %s"
        results = self.execute_query(query, {"hotel_id": hotel_id})
        return results[0] if results else None
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()

# Global instance
snowflake_db = SnowflakeDB() 