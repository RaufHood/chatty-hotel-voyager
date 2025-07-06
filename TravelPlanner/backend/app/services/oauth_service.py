import secrets
from datetime import datetime
from typing import Optional, Dict, Any
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.core.settings import settings
from app.schemas.auth import OAuthProvider, Token
from app.services.jwt_service import jwt_service
from app.services.user_service import user_service

class OAuthService:
    def __init__(self):
        self.oauth = OAuth()
        self._setup_oauth_providers()
    
    def _setup_oauth_providers(self):
        """Setup OAuth providers with their respective configurations"""
        config = Config('.env')
        
        # Google OAuth
        if settings.google_client_id and settings.google_client_secret:
            self.oauth.register(
                name='google',
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
                server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
                client_kwargs={'scope': 'openid email profile'}
            )
        
        # Facebook OAuth
        if settings.facebook_client_id and settings.facebook_client_secret:
            self.oauth.register(
                name='facebook',
                client_id=settings.facebook_client_id,
                client_secret=settings.facebook_client_secret,
                api_base_url='https://graph.facebook.com/',
                access_token_url='https://graph.facebook.com/oauth/access_token',
                authorize_url='https://www.facebook.com/dialog/oauth',
                client_kwargs={'scope': 'email public_profile'}
            )
        
        # GitHub OAuth
        if settings.github_client_id and settings.github_client_secret:
            self.oauth.register(
                name='github',
                client_id=settings.github_client_id,
                client_secret=settings.github_client_secret,
                api_base_url='https://api.github.com/',
                access_token_url='https://github.com/login/oauth/access_token',
                authorize_url='https://github.com/login/oauth/authorize',
                client_kwargs={'scope': 'read:user user:email'}
            )
        
        # Microsoft OAuth
        if settings.microsoft_client_id and settings.microsoft_client_secret:
            self.oauth.register(
                name='microsoft',
                client_id=settings.microsoft_client_id,
                client_secret=settings.microsoft_client_secret,
                api_base_url='https://graph.microsoft.com/v1.0/',
                access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
                authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                client_kwargs={'scope': 'openid email profile'}
            )
    
    def generate_state(self) -> str:
        """Generate a random state parameter for OAuth security"""
        return secrets.token_urlsafe(32)
    
    def get_oauth_url(self, provider: OAuthProvider, state: str) -> str:
        """Get OAuth authorization URL for the specified provider"""
        if provider == OAuthProvider.GOOGLE:
            return self.oauth.google.authorize_redirect(
                redirect_uri=f"{settings.frontend_url}/auth/callback/google",
                state=state
            )
        elif provider == OAuthProvider.FACEBOOK:
            return self.oauth.facebook.authorize_redirect(
                redirect_uri=f"{settings.frontend_url}/auth/callback/facebook",
                state=state
            )
        elif provider == OAuthProvider.GITHUB:
            return self.oauth.github.authorize_redirect(
                redirect_uri=f"{settings.frontend_url}/auth/callback/github",
                state=state
            )
        elif provider == OAuthProvider.MICROSOFT:
            return self.oauth.microsoft.authorize_redirect(
                redirect_uri=f"{settings.frontend_url}/auth/callback/microsoft",
                state=state
            )
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
    
    async def handle_oauth_callback(self, provider: OAuthProvider, code: str) -> Token:
        """Handle OAuth callback and return user token"""
        # Get user info from OAuth provider
        user_info = await self._get_user_info(provider, code)
        
        # Find or create user using Snowflake
        user_data = user_service.get_or_create_user(user_info, provider)
        
        if not user_data:
            raise ValueError("Failed to create or retrieve user")
        
        # Generate standardized JWT token using centralized service
        token = jwt_service.create_token_from_data(user_data)
        
        return token
    

    
    def _get_user_info(self, provider: OAuthProvider, code: str) -> Dict[str, Any]:
        """Get user information from OAuth provider"""
        if provider == OAuthProvider.GOOGLE:
            token = self.oauth.google.authorize_access_token()
            user_info = self.oauth.google.parse_id_token(token)
            return {
                'email': user_info.get('email'),
                'given_name': user_info.get('given_name'),
                'family_name': user_info.get('family_name'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'sub': user_info.get('sub')
            }
        
        elif provider == OAuthProvider.FACEBOOK:
            token = self.oauth.facebook.authorize_access_token()
            resp = self.oauth.facebook.get('/me?fields=id,name,email,picture')
            user_info = resp.json()
            return {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture', {}).get('data', {}).get('url'),
                'id': user_info.get('id')
            }
        
        elif provider == OAuthProvider.GITHUB:
            token = self.oauth.github.authorize_access_token()
            resp = self.oauth.github.get('/user')
            user_info = resp.json()
            return {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'avatar_url': user_info.get('avatar_url'),
                'id': str(user_info.get('id'))
            }
        
        elif provider == OAuthProvider.MICROSOFT:
            token = self.oauth.microsoft.authorize_access_token()
            resp = self.oauth.microsoft.get('/me')
            user_info = resp.json()
            return {
                'email': user_info.get('mail') or user_info.get('userPrincipalName'),
                'name': user_info.get('displayName'),
                'id': user_info.get('id')
            }
        
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

# Global OAuth service instance
oauth_service = OAuthService() 