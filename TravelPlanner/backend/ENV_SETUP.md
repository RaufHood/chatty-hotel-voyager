# Environment Configuration Guide

This guide explains all the environment variables needed for the improved OAuth system with consistent JWT tokens.

## Required .env File Structure

Create a `.env` file in the `backend/` directory with the following variables:

```env
# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/TravelPlanner
REDIS_URL=redis://redis:6379/0

# =============================================================================
# SECURITY & JWT CONFIGURATION
# =============================================================================
# Generate strong secrets for production (use: openssl rand -hex 32)
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# =============================================================================
# OAUTH2 PROVIDER CONFIGURATION
# =============================================================================

# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Facebook OAuth2
FACEBOOK_CLIENT_ID=your-facebook-app-id
FACEBOOK_CLIENT_SECRET=your-facebook-app-secret

# GitHub OAuth2
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Microsoft OAuth2
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
APP_NAME=TravelPlanner
FRONTEND_URL=http://localhost:3000
ENABLE_CELERY=y

# =============================================================================
# AI & ML CONFIGURATION
# =============================================================================
# Add your AI service API keys here
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# =============================================================================
# EXTERNAL SERVICE CONFIGURATION
# =============================================================================
# Payment processing (if using Stripe)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key

# Email service (if using SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com

# =============================================================================
# MONITORING & LOGGING
# =============================================================================
# Sentry for error tracking
SENTRY_DSN=your-sentry-dsn

# Log level
LOG_LEVEL=INFO

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================
# Set to 'development' for debug mode
ENVIRONMENT=development
DEBUG=true

# =============================================================================
# PRODUCTION SETTINGS (override these in production)
# =============================================================================
# Set to 'production' for production mode
# ENVIRONMENT=production
# DEBUG=false
# FRONTEND_URL=https://yourdomain.com
```

## Key Changes from Previous Version

### 🔐 **New Security Variables:**
- `JWT_SECRET_KEY` - Separate secret for JWT tokens (NEW)
- `JWT_ALGORITHM` - JWT signing algorithm (NEW)
- `JWT_EXPIRE_MINUTES` - Token expiration time (NEW)

### 🔄 **Updated OAuth Variables:**
- All OAuth provider variables now support the improved system
- Consistent naming convention across all providers

### 🛡️ **Security Best Practices:**

1. **Generate Strong Secrets:**
   ```bash
   # Generate a strong secret key
   openssl rand -hex 32
   
   # Example output: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
   ```

2. **Use Different Secrets:**
   - `SECRET_KEY` for general application security
   - `JWT_SECRET_KEY` specifically for JWT tokens

3. **Environment-Specific Configuration:**
   - Development: Use localhost URLs
   - Production: Use HTTPS URLs and strong secrets

## OAuth Provider Setup

### Google OAuth2:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Set redirect URI: `http://localhost:3000/auth/callback/google`
4. Copy Client ID and Client Secret

### Facebook OAuth2:
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create app and add Facebook Login
3. Set redirect URI: `http://localhost:3000/auth/callback/facebook`
4. Copy App ID and App Secret

### GitHub OAuth2:
1. Go to [GitHub Settings → OAuth Apps](https://github.com/settings/developers)
2. Create new OAuth App
3. Set callback URL: `http://localhost:3000/auth/callback/github`
4. Copy Client ID and Client Secret

### Microsoft OAuth2:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Register new application
3. Set redirect URI: `http://localhost:3000/auth/callback/microsoft`
4. Copy Application ID and create Client Secret

## Production Deployment

For production, update these variables:

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
FRONTEND_URL=https://yourdomain.com

# Use strong, unique secrets
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-secret-key

# Use HTTPS URLs for OAuth redirects
# Update all OAuth provider redirect URIs to use HTTPS
```

## Validation

After setting up your `.env` file, you can validate the configuration:

```bash
# Test database connection
python -c "from app.services.database import engine; print('Database OK')"

# Test JWT service
python -c "from app.services.jwt_service import jwt_service; print('JWT Service OK')"

# Test OAuth service
python -c "from app.services.oauth_service import oauth_service; print('OAuth Service OK')"
```

## Troubleshooting

### Common Issues:

1. **"JWT_SECRET_KEY not set"**
   - Add `JWT_SECRET_KEY=your-secret-key` to `.env`

2. **"OAuth provider not configured"**
   - Ensure all required OAuth variables are set
   - Check that client IDs and secrets are correct

3. **"Database connection failed"**
   - Verify `DATABASE_URL` is correct
   - Ensure database is running

4. **"Invalid redirect URI"**
   - Check that `FRONTEND_URL` matches your OAuth app configuration
   - Ensure redirect URIs in OAuth providers match your setup 