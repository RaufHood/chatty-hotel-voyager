import pytest
from datetime import datetime, timedelta
from app.services.jwt_service import jwt_service
from app.models.user import User
from app.schemas.auth import OAuthProvider

class TestAuthConsistency:
    """Test that all authentication methods return consistent JWT tokens"""
    
    def test_jwt_token_structure_consistency(self):
        """Test that JWT tokens have consistent structure across all auth methods"""
        # Create a test user
        test_user = User(
            id=1,
            email="test@example.com",
            full_name="Test User",
            oauth_provider=OAuthProvider.GOOGLE,
            oauth_id="12345",
            is_active=True
        )
        
        # Generate token using centralized service
        token_response = jwt_service.create_token(test_user)
        
        # Verify token structure
        assert token_response.access_token is not None
        assert token_response.token_type == "bearer"
        assert token_response.expires_in > 0
        assert token_response.refresh_token is not None
        assert token_response.user is not None
        
        # Verify JWT payload structure
        payload = jwt_service.verify_token(token_response.access_token)
        assert payload is not None
        
        # Check required fields are present
        required_fields = ["sub", "email", "oauth_provider", "oauth_id", "iat", "exp", "type"]
        for field in required_fields:
            assert field in payload
        
        # Verify field values
        assert payload["sub"] == str(test_user.id)
        assert payload["email"] == test_user.email
        assert payload["oauth_provider"] == test_user.oauth_provider.value
        assert payload["oauth_id"] == test_user.oauth_id
        assert payload["type"] == "access"
    
    def test_token_verification_consistency(self):
        """Test that token verification works consistently"""
        test_user = User(
            id=2,
            email="verify@example.com",
            full_name="Verify User",
            oauth_provider=OAuthProvider.FACEBOOK,
            oauth_id="67890",
            is_active=True
        )
        
        # Create token
        token_response = jwt_service.create_token(test_user)
        
        # Verify token can be verified
        payload = jwt_service.verify_token(token_response.access_token)
        assert payload is not None
        
        # Verify user ID extraction works
        user_id = jwt_service.extract_user_id_from_token(token_response.access_token)
        assert user_id == test_user.id
    
    def test_refresh_token_consistency(self):
        """Test that refresh tokens work consistently"""
        test_user = User(
            id=3,
            email="refresh@example.com",
            full_name="Refresh User",
            oauth_provider=OAuthProvider.GITHUB,
            oauth_id="11111",
            is_active=True
        )
        
        # Create access token with refresh token
        token_response = jwt_service.create_token(test_user)
        
        # Verify refresh token
        refresh_payload = jwt_service.verify_refresh_token(token_response.refresh_token)
        assert refresh_payload is not None
        assert refresh_payload["type"] == "refresh"
        assert refresh_payload["sub"] == str(test_user.id)
        assert refresh_payload["email"] == test_user.email
    
    def test_different_oauth_providers_consistency(self):
        """Test that tokens are consistent across different OAuth providers"""
        providers = [OAuthProvider.GOOGLE, OAuthProvider.FACEBOOK, OAuthProvider.GITHUB, OAuthProvider.MICROSOFT]
        
        for i, provider in enumerate(providers):
            test_user = User(
                id=100 + i,
                email=f"user{i}@example.com",
                full_name=f"User {i}",
                oauth_provider=provider,
                oauth_id=f"oauth_{i}",
                is_active=True
            )
            
            # Create token
            token_response = jwt_service.create_token(test_user)
            
            # Verify token structure is consistent
            payload = jwt_service.verify_token(token_response.access_token)
            assert payload is not None
            assert payload["oauth_provider"] == provider.value
            assert payload["oauth_id"] == f"oauth_{i}"
            assert payload["type"] == "access"
    
    def test_token_expiration_consistency(self):
        """Test that token expiration is handled consistently"""
        test_user = User(
            id=4,
            email="expire@example.com",
            full_name="Expire User",
            oauth_provider=OAuthProvider.MICROSOFT,
            oauth_id="22222",
            is_active=True
        )
        
        # Create token
        token_response = jwt_service.create_token(test_user)
        
        # Verify token is valid initially
        payload = jwt_service.verify_token(token_response.access_token)
        assert payload is not None
        
        # Verify expiration time is in the future
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        assert exp_datetime > datetime.utcnow()
    
    def test_invalid_token_handling(self):
        """Test that invalid tokens are handled consistently"""
        # Test with invalid token
        invalid_token = "invalid.jwt.token"
        payload = jwt_service.verify_token(invalid_token)
        assert payload is None
        
        # Test with expired token (this would require mocking time)
        # For now, just test that None is returned for invalid tokens
        payload = jwt_service.verify_token("")
        assert payload is None 