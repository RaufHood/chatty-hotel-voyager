#!/usr/bin/env python3
"""
Test script to verify Snowflake connection
Run this script to test if your Snowflake configuration is correct
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_snowflake_connection():
    """Test Snowflake connection with current environment variables"""
    
    # Get Snowflake configuration
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    database = os.getenv('SNOWFLAKE_DATABASE')
    schema = os.getenv('SNOWFLAKE_SCHEMA')
    role = os.getenv('SNOWFLAKE_ROLE')
    
    print("🔍 Checking Snowflake Configuration:")
    print(f"   Account: {account}")
    print(f"   User: {user}")
    print(f"   Warehouse: {warehouse}")
    print(f"   Database: {database}")
    print(f"   Schema: {schema}")
    print(f"   Role: {role}")
    print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
    
    # Check if all required fields are set
    required_fields = ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD']
    missing_fields = [field for field in required_fields if not os.getenv(field)]
    
    if missing_fields:
        print(f"\n❌ Missing required environment variables: {missing_fields}")
        print("Please set these in your .env file")
        return False
    
    try:
        # Try to import and connect to Snowflake
        import snowflake.connector
        
        print("\n🔌 Attempting to connect to Snowflake...")
        
        # Create connection
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        
        print(f"✅ Successfully connected to Snowflake!")
        print(f"   Version: {version}")
        
        # Test if our tables exist
        print("\n📋 Checking for required tables...")
        
        # Get table names from settings
        from app.core.settings import settings
        tables_to_check = [
            settings.snowflake_users_table,
            settings.snowflake_hotels_table,
            settings.snowflake_trips_table,
            settings.snowflake_trip_legs_table
        ]
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {table}: {count} rows")
            except Exception as e:
                print(f"   ❌ {table}: {str(e)}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Snowflake connection test completed successfully!")
        return True
        
    except ImportError:
        print("\n❌ Snowflake connector not installed!")
        print("Run: pip install snowflake-connector-python[pandas]")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your account identifier format")
        print("2. Verify username and password")
        print("3. Ensure warehouse exists and is accessible")
        print("4. Check if your role has necessary permissions")
        return False

if __name__ == "__main__":
    print("🚀 Snowflake Connection Test")
    print("=" * 40)
    
    success = test_snowflake_connection()
    
    if success:
        print("\n✅ Your Snowflake configuration is working correctly!")
        print("You can now use the TravelPlanner application with Snowflake.")
    else:
        print("\n❌ Please fix the configuration issues above before proceeding.")
        sys.exit(1) 