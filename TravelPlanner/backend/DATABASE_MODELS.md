# Database Models and Snowflake Integration

This document describes the data models and database integration for the TravelPlanner application.

## Overview

The application uses Snowflake as the primary database for storing user data, hotels, trips, and trip legs. The models are designed to match the existing Snowflake schema while providing additional functionality for OAuth integration.

## Database Schema

### Users Table
```sql
CREATE TABLE CHATTY_HOTEL_VOYAGER.DBO.USERS (
    USER_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    EMAIL VARCHAR(30),
    NAME VARCHAR(30),
    SURNAME VARCHAR(30),
    AUTO_TOKEN VARCHAR(255),
    primary key (USER_ID)
);
```

### Hotels Table
```sql
CREATE TABLE CHATTY_HOTEL_VOYAGER.DBO.HOTELS (
    HOTEL_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    HOTEL_NAME VARCHAR(255),
    STARS NUMBER(38,0),
    RATING FLOAT,
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    COUNTRY_CODE VARCHAR(5),
    CITY_CODE VARCHAR(5),
    HOTEL_TYPE VARCHAR(50),
    primary key (HOTEL_ID)
);
```

### Trips Table
```sql
CREATE TABLE CHATTY_HOTEL_VOYAGER.DBO.TRIPS (
    TRIP_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    USER_ID NUMBER(38,0),
    DATE_START TIMESTAMP_NTZ(9),
    DATE_END TIMESTAMP_NTZ(9),
    primary key (TRIP_ID),
    foreign key (USER_ID) references CHATTY_HOTEL_VOYAGER.DBO.USERS(USER_ID)
);
```

### Trip Legs Table
```sql
CREATE TABLE CHATTY_HOTEL_VOYAGER.DBO.TRIP_LEGS (
    TRIP_LEG_ID NUMBER(38,0) NOT NULL autoincrement start 1 increment 1 noorder,
    TRIP_ID NUMBER(38,0),
    USER_ID NUMBER(38,0),
    HOTEL_ID NUMBER(38,0),
    ARRIVAL_DATE TIMESTAMP_NTZ(9),
    DEPARTURE_DATE TIMESTAMP_NTZ(9),
    STAY_PRICE FLOAT,
    primary key (TRIP_LEG_ID),
    foreign key (TRIP_ID) references CHATTY_HOTEL_VOYAGER.DBO.TRIPS(TRIP_ID),
    foreign key (USER_ID) references CHATTY_HOTEL_VOYAGER.DBO.USERS(USER_ID),
    foreign key (HOTEL_ID) references CHATTY_HOTEL_VOYAGER.DBO.HOTELS(HOTEL_ID)
);
```

## Application Models

### User Model
- **File**: `app/models/user.py`
- **Table**: `USERS`
- **Fields**: Matches Snowflake schema with additional OAuth fields
- **Relationships**: One-to-many with Trips and TripLegs

### Hotel Model
- **File**: `app/models/hotel.py`
- **Table**: `HOTELS`
- **Fields**: Matches Snowflake schema exactly
- **Relationships**: One-to-many with TripLegs

### Trip Model
- **File**: `app/models/trip.py`
- **Table**: `TRIPS`
- **Fields**: Matches Snowflake schema exactly
- **Relationships**: Many-to-one with User, One-to-many with TripLegs

### TripLeg Model
- **File**: `app/models/trip_leg.py`
- **Table**: `TRIP_LEGS`
- **Fields**: Matches Snowflake schema exactly
- **Relationships**: Many-to-one with User, Trip, and Hotel

## Database Services

### SnowflakeDB Service
- **File**: `app/services/snowflake_db.py`
- **Purpose**: Handles all Snowflake database operations
- **Features**:
  - Connection management
  - Query execution
  - Data insertion/updates
  - User-specific operations

### User Service
- **File**: `app/services/user_service.py`
- **Purpose**: High-level user operations
- **Features**:
  - OAuth integration
  - User creation/retrieval
  - JWT token management

## Configuration

### Environment Variables
Add the following to your `.env` file:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=CHATTY_HOTEL_VOYAGER
SNOWFLAKE_SCHEMA=DBO
SNOWFLAKE_ROLE=your_role
```

## API Schemas

### User Schemas
- **UserBase**: Base user fields
- **UserCreate**: For creating new users
- **UserUpdate**: For updating user information
- **UserResponse**: For API responses

### Hotel Schemas
- **HotelBase**: Base hotel fields
- **HotelCreate**: For creating new hotels
- **HotelUpdate**: For updating hotel information
- **HotelResponse**: For API responses

### Trip Schemas
- **TripBase**: Base trip fields
- **TripCreate**: For creating new trips
- **TripUpdate**: For updating trip information
- **TripResponse**: For API responses

### TripLeg Schemas
- **TripLegBase**: Base trip leg fields
- **TripLegCreate**: For creating new trip legs
- **TripLegUpdate**: For updating trip leg information
- **TripLegResponse**: For API responses

## OAuth Integration

The application integrates OAuth authentication with the Snowflake database:

1. **User Authentication**: OAuth providers (Google, Facebook, GitHub, Microsoft) authenticate users
2. **User Creation**: New users are created in Snowflake with OAuth data
3. **Token Generation**: JWT tokens are generated and stored as `AUTO_TOKEN`
4. **Consistent Tokens**: All authentication methods return the same JWT token format

## Testing

Run the model tests to verify everything works:

```bash
cd backend
pytest app/tests/test_models.py -v
```

## Dependencies

The following packages are required for Snowflake integration:

```
snowflake-connector-python[pandas]>=3.0.0
pandas>=2.0.0
```

## Usage Examples

### Creating a User
```python
from app.services.user_service import user_service
from app.schemas.user import UserCreate

user_data = UserCreate(
    email="user@example.com",
    name="John",
    surname="Doe",
    oauth_provider=OAuthProvider.GOOGLE,
    oauth_id="123456789"
)

user = user_service.create_user_from_oauth(user_data)
```

### Getting User by Email
```python
user = user_service.get_user_by_email("user@example.com")
```

### Updating User
```python
from app.schemas.user import UserUpdate

update_data = UserUpdate(name="Jane")
success = user_service.update_user(user_id, update_data)
```

## Notes

- All models use SQLModel for ORM functionality
- Field aliases are used to match Snowflake column names
- Relationships are defined for easy querying
- The `AUTO_TOKEN` field stores JWT tokens for authentication
- OAuth provider information is not stored in Snowflake but handled in the application layer 