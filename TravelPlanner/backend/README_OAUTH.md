# OAuth2 Authentication Setup

This document explains how to set up OAuth2 authentication for multiple providers in the TravelPlanner application.

## Supported OAuth Providers

- Google
- Facebook
- GitHub
- Microsoft

## Environment Variables

Add the following environment variables to your `.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/TravelPlanner
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# OAuth2 Configuration

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Facebook OAuth
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# Frontend URL for OAuth redirects
FRONTEND_URL=http://localhost:3000

# App Configuration
APP_NAME=TravelPlanner
ENABLE_CELERY=y
```

## OAuth Provider Setup

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Set authorized redirect URIs to: `http://localhost:3000/auth/callback/google`
6. Copy Client ID and Client Secret to your `.env` file

### Facebook OAuth
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login product
4. Set Valid OAuth Redirect URIs to: `http://localhost:3000/auth/callback/facebook`
5. Copy App ID and App Secret to your `.env` file

### GitHub OAuth
1. Go to [GitHub Settings → Developer settings → OAuth Apps](https://github.com/settings/developers)
2. Create a new OAuth App
3. Set Authorization callback URL to: `http://localhost:3000/auth/callback/github`
4. Copy Client ID and Client Secret to your `.env` file

### Microsoft OAuth
1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Set redirect URI to: `http://localhost:3000/auth/callback/microsoft`
4. Copy Application (client) ID and create a client secret
5. Add both to your `.env` file

## API Endpoints

### Authentication Endpoints

- `GET /api/auth/providers` - Get available OAuth providers
- `POST /api/auth/login/{provider}` - Initiate OAuth login
- `POST /api/auth/callback/{provider}` - Handle OAuth callback
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/refresh` - Refresh JWT token (requires current user)
- `POST /api/auth/refresh-token` - Refresh JWT token using refresh token

### Usage Example

1. **Get available providers:**
   ```bash
   curl http://localhost:8000/api/auth/providers
   ```

2. **Initiate Google login:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/google
   ```

3. **Handle callback (frontend):**
   ```javascript
   // After user authorizes, you'll get a code
   const response = await fetch('/api/auth/callback/google', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ code: 'authorization_code', state: 'state' })
   });
   const token = await response.json();
   // Response includes: access_token, refresh_token, expires_in, user info
   ```

4. **Use token for authenticated requests:**
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/auth/me
   ```

5. **Refresh token when expired:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/refresh-token \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "your_refresh_token"}'
   ```

## Frontend Integration

The OAuth flow works as follows:

1. User clicks "Login with [Provider]"
2. Frontend calls `/api/auth/login/{provider}` to get authorization URL
3. Frontend redirects user to the authorization URL
4. User authorizes the application
5. Provider redirects back to frontend with authorization code
6. Frontend calls `/api/auth/callback/{provider}` with the code
7. Backend returns JWT token
8. Frontend stores token and uses it for authenticated requests

## JWT Token Format

All authentication methods return consistent JWT tokens with the following structure:

### Access Token Payload:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "oauth_provider": "google|facebook|github|microsoft",
  "oauth_id": "provider_user_id",
  "iat": "issued_at_timestamp",
  "exp": "expiration_timestamp",
  "type": "access"
}
```

### Token Response:
```json
{
  "access_token": "jwt_token_string",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "refresh_token_string",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "User Name",
    "avatar_url": "https://...",
    "oauth_provider": "google",
    "oauth_id": "12345",
    "is_active": true
  }
}
```

## Security Notes

- Always use HTTPS in production
- Store JWT tokens securely (httpOnly cookies recommended)
- Store refresh tokens securely and separately from access tokens
- Implement CSRF protection
- Use strong secret keys
- Regularly rotate client secrets
- Implement proper error handling
- Add rate limiting for auth endpoints
- Access tokens expire in 30 minutes by default
- Refresh tokens expire in 7 days by default 