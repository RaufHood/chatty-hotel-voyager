# Database Setup Documentation

## Overview

The TravelPlanner application uses **Snowflake** as its primary database. The database connection is automatically initialized when the application starts up.

## Database Architecture

### Connection Management
- **Single Connection**: One persistent connection to Snowflake per application instance
- **Lazy Initialization**: Database connection is established only when needed
- **Automatic Cleanup**: Connection is properly closed when the application shuts down

### Key Components

1. **`database.py`** - Main database interface and connection management
2. **`snowflake_db.py`** - Snowflake-specific database operations
3. **`user_service.py`** - User-related database operations

## Configuration

### Environment Variables

Set these environment variables in your `.env` file:

```env
# Snowflake Database Settings
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=your_database_name
SNOWFLAKE_SCHEMA=your_schema_name
SNOWFLAKE_ROLE=your_role_name  # Optional
```

### Settings Configuration

The database settings are managed in `app/core/settings.py`:

```python
# Snowflake Database Settings
snowflake_account: Optional[str] = os.getenv("SNOWFLAKE_ACCOUNT")
snowflake_user: Optional[str] = os.getenv("SNOWFLAKE_USER")
snowflake_password: Optional[str] = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_warehouse: Optional[str] = os.getenv("SNOWFLAKE_WAREHOUSE")
snowflake_database: Optional[str] = os.getenv("SNOWFLAKE_DATABASE")
snowflake_schema: Optional[str] = os.getenv("SNOWFLAKE_SCHEMA")
snowflake_role: Optional[str] = os.getenv("SNOWFLAKE_ROLE")

# Table Names
snowflake_users_table: str = "USERS"
snowflake_hotels_table: str = "HOTELS"
snowflake_trips_table: str = "TRIPS"
snowflake_trip_legs_table: str = "TRIP_LEGS"
```

## Database Operations

### Connection Management

```python
from app.services.database import get_database, get_db_session

# Get database instance
db = get_database()

# Use context manager for sessions
with get_db_session() as db:
    # Perform database operations
    result = db.execute_query("SELECT * FROM USERS")
```

### Basic Operations

```python
# Execute queries
results = db.execute_query("SELECT * FROM USERS WHERE EMAIL = %s", {"email": "user@example.com"})

# Execute inserts
affected_rows = db.execute_insert("INSERT INTO USERS (EMAIL, NAME) VALUES (%s, %s)", {"email": "new@example.com", "name": "John"})

# Execute updates
affected_rows = db.execute_update("UPDATE USERS SET NAME = %s WHERE EMAIL = %s", {"name": "Jane", "email": "user@example.com"})

# Execute deletes
affected_rows = db.execute_delete("DELETE FROM USERS WHERE EMAIL = %s", {"email": "user@example.com"})
```

### User Operations

```python
from app.services.user_service import user_service

# Get user by email
user = user_service.get_user_by_email("user@example.com")

# Get user by ID
user = user_service.get_user_by_id(123)

# Update user
user_update = UserUpdate(name="New Name")
success = user_service.update_user(123, user_update)
```

## Table Structure

### Users Table

```sql
CREATE TABLE USERS (
    USER_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    EMAIL VARCHAR(255) UNIQUE NOT NULL,
    NAME VARCHAR(255) NOT NULL,
    SURNAME VARCHAR(255) NOT NULL,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### Future Tables

The following tables are planned but not yet implemented:
- **HOTELS** - Hotel information and availability
- **TRIPS** - User trip data
- **TRIP_LEGS** - Individual trip segments

## Application Lifecycle

### Startup
1. Application starts
2. Database connection is initialized
3. Connection is tested
4. Tables are created if they don't exist
5. Application is ready to serve requests

### Runtime
- Database connection is maintained throughout the application lifecycle
- Services use the shared database instance
- Connection pooling is handled by Snowflake connector

### Shutdown
1. Application receives shutdown signal
2. Database connection is properly closed
3. Application terminates cleanly

## Testing

### Run Database Tests

```bash
cd backend
python test_database.py
```

This will test:
- Database connection
- User operations
- Table creation
- Environment configuration

### Manual Testing

```python
from app.services.database import init_database, test_connection

# Initialize database
db = init_database()

# Test connection
test_connection()

# Execute test query
result = db.execute_query("SELECT CURRENT_VERSION()")
print(f"Snowflake version: {result[0]['CURRENT_VERSION()']}")
```

## Error Handling

### Connection Errors
- Missing environment variables are logged as warnings
- Connection failures are logged as errors
- Application continues running even if database fails to initialize

### Query Errors
- All database operations are wrapped in try-catch blocks
- Errors are logged with context
- Failed operations return appropriate default values (None, False, etc.)

## Monitoring

### Logging
Database operations are logged with appropriate levels:
- **INFO**: Successful operations, connection status
- **WARNING**: Missing configuration, non-critical issues
- **ERROR**: Connection failures, query errors

### Health Check
The application includes a health check endpoint that can verify database connectivity:

```bash
curl http://localhost:8000/api/chat/health
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check environment variables
   - Verify Snowflake credentials
   - Ensure network connectivity

2. **Missing Tables**
   - Tables are created automatically on startup
   - Check logs for table creation errors
   - Verify schema permissions

3. **Permission Errors**
   - Ensure user has proper Snowflake role
   - Check warehouse, database, and schema access
   - Verify table permissions

### Debug Mode

Enable debug logging to see detailed database operations:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

1. **Credentials**: Store Snowflake credentials securely in environment variables
2. **Connection**: Use SSL/TLS for database connections
3. **Permissions**: Follow principle of least privilege for database users
4. **Logging**: Avoid logging sensitive data in production

## Performance

1. **Connection Pooling**: Snowflake connector handles connection pooling
2. **Query Optimization**: Use parameterized queries to prevent SQL injection
3. **Caching**: Consider implementing application-level caching for frequently accessed data
4. **Monitoring**: Monitor query performance and connection usage 