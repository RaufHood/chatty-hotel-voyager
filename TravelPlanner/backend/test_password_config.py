#!/usr/bin/env python3
"""
Test script to verify password configuration
This helps ensure special characters in passwords are handled correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_password_configuration():
    """Test that password is being read correctly from .env"""
    
    print("🔐 Password Configuration Test")
    print("=" * 40)
    
    # Get password from environment
    password = os.getenv('SNOWFLAKE_PASSWORD')
    
    if not password:
        print("❌ SNOWFLAKE_PASSWORD not found in .env file")
        print("\n📝 Make sure your .env file contains:")
        print('SNOWFLAKE_PASSWORD="your_password_here"')
        return False
    
    # Show password length and first/last characters (for verification)
    print(f"✅ Password found!")
    print(f"   Length: {len(password)} characters")
    print(f"   First character: '{password[0]}'")
    print(f"   Last character: '{password[-1]}'")
    
    # Check for common special characters
    special_chars = ['#', '@', '%', '&', '!', '$', '^', '*', '(', ')', '+', '=', '[', ']', '{', '}', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/']
    found_chars = [char for char in special_chars if char in password]
    
    if found_chars:
        print(f"   Contains special characters: {found_chars}")
        print("   ✅ Special characters detected - make sure you used quotes in .env")
    else:
        print("   No special characters detected")
    
    # Test other required fields
    print("\n🔍 Checking other required fields:")
    
    required_fields = {
        'SNOWFLAKE_ACCOUNT': 'Account identifier',
        'SNOWFLAKE_USER': 'Username',
        'SNOWFLAKE_WAREHOUSE': 'Warehouse name',
        'SNOWFLAKE_DATABASE': 'Database name',
        'SNOWFLAKE_SCHEMA': 'Schema name',
        'SNOWFLAKE_ROLE': 'Role name'
    }
    
    missing_fields = []
    for field, description in required_fields.items():
        value = os.getenv(field)
        if value:
            print(f"   ✅ {description}: {value}")
        else:
            print(f"   ❌ {description}: NOT SET")
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n⚠️  Missing fields: {missing_fields}")
        print("Please add these to your .env file")
        return False
    
    print("\n🎉 All required fields are configured!")
    return True

def show_env_examples():
    """Show examples of correct .env configurations"""
    
    print("\n📝 Example .env configurations:")
    
    print("\n1. Simple password (no special characters):")
    print("""
SNOWFLAKE_PASSWORD=mypassword123
""")
    
    print("\n2. Password with hash (#):")
    print("""
SNOWFLAKE_PASSWORD="my#password123"
""")
    
    print("\n3. Password with at symbol (@):")
    print("""
SNOWFLAKE_PASSWORD="my@password123"
""")
    
    print("\n4. Complex password with multiple special characters:")
    print("""
SNOWFLAKE_PASSWORD="My#Complex@Password%2024!"
""")
    
    print("\n5. Password with spaces:")
    print("""
SNOWFLAKE_PASSWORD="my password with spaces"
""")

if __name__ == "__main__":
    success = test_password_configuration()
    show_env_examples()
    
    if success:
        print("\n✅ Your password configuration looks good!")
        print("You can now run the Snowflake connection test:")
        print("python test_snowflake_connection.py")
    else:
        print("\n❌ Please fix the configuration issues above.") 