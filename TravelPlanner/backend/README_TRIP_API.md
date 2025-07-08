# Trip API Documentation

## Overview

The Trip API provides endpoints for managing user trips, trip legs, and hotel bookings in the TravelPlanner application. The API interacts with Snowflake database tables to store and retrieve trip information.

## Database Schema

### TRIPS Table
```sql
CREATE TABLE CHATTY_HOTEL_VOYAGER.DBO.TRIPS (
    TRIP_ID NUMBER(38,0) NOT NULL AUTOINCREMENT START 1 INCREMENT 1 NOORDER,
    USER_ID NUMBER(38,0),
    DATE_START TIMESTAMP_NTZ(9),
    DATE_END TIMESTAMP_NTZ(9),
    PRIMARY KEY (TRIP_ID),
    FOREIGN KEY (USER_ID) REFERENCES CHATTY_HOTEL_VOYAGER.DBO.USERS(USER_ID)
);
```

### TRIP_LEGS Table
```sql
CREATE TABLE CHATTY_HOTEL_VOYAGER.DBO.TRIP_LEGS (
    TRIP_LEG_ID NUMBER(38,0) NOT NULL AUTOINCREMENT START 1 INCREMENT 1 NOORDER,
    TRIP_ID NUMBER(38,0),
    USER_ID NUMBER(38,0),
    HOTEL_ID NUMBER(38,0),
    ARRIVAL_DATE TIMESTAMP_NTZ(9),
    DEPARTURE_DATE TIMESTAMP_NTZ(9),
    STAY_PRICE FLOAT,
    PRIMARY KEY (TRIP_LEG_ID),
    FOREIGN KEY (TRIP_ID) REFERENCES CHATTY_HOTEL_VOYAGER.DBO.TRIPS(TRIP_ID),
    FOREIGN KEY (USER_ID) REFERENCES CHATTY_HOTEL_VOYAGER.DBO.USERS(USER_ID),
    FOREIGN KEY (HOTEL_ID) REFERENCES CHATTY_HOTEL_VOYAGER.DBO.HOTELS(HOTEL_ID)
);
```

### HOTELS Table
```sql
CREATE TABLE CHATTY_HOTEL_VOYAGER.DBO.HOTELS (
    HOTEL_ID NUMBER(38,0) NOT NULL AUTOINCREMENT START 1 INCREMENT 1 NOORDER,
    HOTEL_NAME VARCHAR(255),
    STARS NUMBER(38,0),
    RATING FLOAT,
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    COUNTRY_CODE VARCHAR(5),
    CITY_CODE VARCHAR(5),
    HOTEL_TYPE VARCHAR(50),
    PRIMARY KEY (HOTEL_ID)
);
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/trips
```

### 1. List Trips
**GET** `/api/trips/`

List all trips or filter by user ID.

**Query Parameters:**
- `user_id` (optional): Filter trips by specific user ID

**Response:**
```json
[
  {
    "trip_id": 1,
    "user_id": 1,
    "date_start": "2024-01-15T00:00:00",
    "date_end": "2024-01-22T00:00:00"
  }
]
```

**Example:**
```bash
# List all trips
curl -X GET "http://localhost:8000/api/trips/"

# List trips for user 1
curl -X GET "http://localhost:8000/api/trips/?user_id=1"
```

### 2. Get Trip by ID
**GET** `/api/trips/{trip_id}`

Get a specific trip by its ID.

**Path Parameters:**
- `trip_id`: The ID of the trip to retrieve

**Response:**
```json
{
  "trip_id": 1,
  "user_id": 1,
  "date_start": "2024-01-15T00:00:00",
  "date_end": "2024-01-22T00:00:00"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/trips/1"
```

### 3. Get Trip Legs
**GET** `/api/trips/{trip_id}/legs`

Get all trip legs for a specific trip, including hotel information.

**Path Parameters:**
- `trip_id`: The ID of the trip

**Response:**
```json
[
  {
    "trip_leg_id": 1,
    "trip_id": 1,
    "user_id": 1,
    "hotel_id": 1,
    "arrival_date": "2024-01-15T14:00:00",
    "departure_date": "2024-01-18T11:00:00",
    "stay_price": 299.99,
    "hotel_name": "Grand Hotel",
    "stars": 4,
    "rating": 4.5,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "country_code": "US",
    "city_code": "NYC",
    "hotel_type": "Luxury"
  }
]
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/trips/1/legs"
```

### 4. Get Trip Hotels
**GET** `/api/trips/{trip_id}/hotels`

Get all hotels booked in a specific trip.

**Path Parameters:**
- `trip_id`: The ID of the trip

**Response:**
```json
{
  "hotels": [
    {
      "hotel_id": 1,
      "hotel_name": "Grand Hotel",
      "stars": 4,
      "rating": 4.5,
      "latitude": 40.7128,
      "longitude": -74.0060,
      "country_code": "US",
      "city_code": "NYC",
      "hotel_type": "Luxury",
      "arrival_date": "2024-01-15T14:00:00",
      "departure_date": "2024-01-18T11:00:00",
      "stay_price": 299.99
    }
  ]
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/trips/1/hotels"
```

### 5. Create Trip
**POST** `/api/trips/`

Create a new trip.

**Request Body:**
```json
{
  "user_id": 1,
  "date_start": "2024-01-15T00:00:00",
  "date_end": "2024-01-22T00:00:00"
}
```

**Response:**
```json
{
  "trip_id": 2,
  "message": "Trip created successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/trips/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "date_start": "2024-01-15T00:00:00",
    "date_end": "2024-01-22T00:00:00"
  }'
```

### 6. Add Trip Leg
**POST** `/api/trips/{trip_id}/legs`

Add a trip leg (hotel booking) to an existing trip.

**Path Parameters:**
- `trip_id`: The ID of the trip

**Request Body:**
```json
{
  "trip_id": 1,
  "user_id": 1,
  "hotel_id": 1,
  "arrival_date": "2024-01-15T14:00:00",
  "departure_date": "2024-01-18T11:00:00",
  "stay_price": 299.99
}
```

**Response:**
```json
{
  "trip_leg_id": 1,
  "message": "Trip leg added successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/trips/1/legs" \
  -H "Content-Type: application/json" \
  -d '{
    "trip_id": 1,
    "user_id": 1,
    "hotel_id": 1,
    "arrival_date": "2024-01-15T14:00:00",
    "departure_date": "2024-01-18T11:00:00",
    "stay_price": 299.99
  }'
```

## Database Functions

The following functions are available in the `SnowflakeDB` class:

### 1. `list_trips(user_id: int) -> List[Dict[str, Any]]`
List all trips for a specific user.

### 2. `get_trip_by_id(trip_id: int) -> Optional[Dict[str, Any]]`
Get a specific trip by trip_id.

### 3. `get_trip_legs(trip_id: int) -> List[Dict[str, Any]]`
Get all trip legs for a specific trip, including hotel information.

### 4. `get_hotels_in_trip(trip_id: int) -> List[Dict[str, Any]]`
Get all hotels booked in a specific trip.

### 5. `create_trip(user_id: int, date_start: str, date_end: str) -> int`
Create a new trip and return the trip_id.

### 6. `add_trip_leg(trip_id: int, user_id: int, hotel_id: int, arrival_date: str, departure_date: str, stay_price: float) -> int`
Add a trip leg to a trip and return the trip_leg_id.

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Request successful
- `404 Not Found`: Trip not found
- `500 Internal Server Error`: Database or server error

Error responses include a detail message:
```json
{
  "detail": "Trip not found"
}
```

## Testing

Use the provided test script to verify the API functionality:

```bash
python test_trip_api.py
```

## Notes

- The API currently operates without authentication (as per AUTH_REMOVAL_SUMMARY.md)
- In production, implement proper authentication and authorization
- All timestamps are in ISO format
- The API uses Pydantic schemas for request/response validation
- Database connections are managed through the SnowflakeDB service 