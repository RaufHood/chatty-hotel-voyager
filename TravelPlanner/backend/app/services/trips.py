from .snowflake_db import get_snowflake_connection
from typing import Any, List, Dict, Optional
from app.core.settings import settings

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