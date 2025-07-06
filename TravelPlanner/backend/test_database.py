#!/usr/bin/env python3
"""
Test script to verify database connection and functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.database import init_database, get_database, test_connection
from app.services.user_service import user_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_database_connection():
    """Test basic database connection"""
    print("🧪 Testing Database Connection")
    print("=" * 40)
    
    try:
        # Initialize database
        print("1. Initializing database...")
        db = init_database()
        print("   ✅ Database initialized successfully")
        
        # Test connection
        print("2. Testing connection...")
        test_connection()
        print("   ✅ Connection test passed")
        
        # Test basic query
        print("3. Testing basic query...")
        result = db.execute_query("SELECT CURRENT_TIMESTAMP() as current_time")
        print(f"   ✅ Query successful: {result[0]['CURRENT_TIME']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_user_operations():
    """Test user-related database operations"""
    print("\n👤 Testing User Operations")
    print("=" * 40)
    
    try:
        # Test getting database instance
        print("1. Getting database instance...")
        db = get_database()
        print("   ✅ Database instance retrieved")
        
        # Test user service
        print("2. Testing user service...")
        
        # Test getting user by email (should return None for non-existent user)
        test_email = "test@example.com"
        user = user_service.get_user_by_email(test_email)
        if user is None:
            print(f"   ✅ User not found (expected): {test_email}")
        else:
            print(f"   ⚠️  User found: {user}")
        
        # Test getting user by ID (should return None for non-existent user)
        test_user_id = 999999
        user = user_service.get_user_by_id(test_user_id)
        if user is None:
            print(f"   ✅ User not found (expected): ID {test_user_id}")
        else:
            print(f"   ⚠️  User found: {user}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ User operations test failed: {e}")
        return False

def test_table_creation():
    """Test table creation functionality"""
    print("\n📋 Testing Table Creation")
    print("=" * 40)
    
    try:
        from app.services.database import create_tables_if_not_exist
        from app.core.settings import settings
        
        print("1. Checking table existence...")
        db = get_database()
        
        # Check if users table exists
        check_query = f"""
        SELECT COUNT(*) as table_count 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = '{settings.snowflake_schema}' 
        AND TABLE_NAME = '{settings.snowflake_users_table}'
        """
        
        result = db.execute_query(check_query)
        table_count = result[0]['TABLE_COUNT']
        
        if table_count > 0:
            print(f"   ✅ {settings.snowflake_users_table} table exists")
        else:
            print(f"   ⚠️  {settings.snowflake_users_table} table does not exist")
            print("   Creating table...")
            create_tables_if_not_exist(db)
            print("   ✅ Table creation completed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Table creation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Database Tests")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Environment Check:")
    required_vars = [
        'SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD',
        'SNOWFLAKE_WAREHOUSE', 'SNOWFLAKE_DATABASE', 'SNOWFLAKE_SCHEMA'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * len(value)} (hidden)")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        print("   Some tests may fail without proper configuration")
    
    print("\n" + "=" * 50)
    
    # Run tests
    tests = [
        ("Database Connection", test_database_connection),
        ("User Operations", test_user_operations),
        ("Table Creation", test_table_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Database is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your configuration and try again.")

if __name__ == "__main__":
    main() 