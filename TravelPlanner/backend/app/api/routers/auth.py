from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.schemas.auth import (
    OAuthProvider, 
    OAuthLoginRequest, 
    OAuthURLResponse, 
    LoginResponse,
    Token,
    RefreshTokenRequest
)
from app.services.oauth_service import oauth_service
from app.services.database import get_session
from app.services.auth_deps import get_current_user
from app.services.jwt_service import jwt_service
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/providers")
async def get_available_providers():
    """Get list of available OAuth providers"""
    providers = []
    
    if oauth_service.oauth.google:
        providers.append({"name": "Google", "id": "google"})
    if oauth_service.oauth.facebook:
        providers.append({"name": "Facebook", "id": "facebook"})
    if oauth_service.oauth.github:
        providers.append({"name": "GitHub", "id": "github"})
    if oauth_service.oauth.microsoft:
        providers.append({"name": "Microsoft", "id": "microsoft"})
    
    return {"providers": providers}

@router.post("/login/{provider}")
async def initiate_oauth_login(
    provider: OAuthProvider,
    db: Session = Depends(get_session)
) -> OAuthURLResponse:
    """Initiate OAuth login for the specified provider"""
    try:
        state = oauth_service.generate_state()
        auth_url = oauth_service.get_oauth_url(provider, state)
        
        return OAuthURLResponse(
            auth_url=auth_url,
            state=state
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/callback/{provider}")
async def oauth_callback(
    provider: OAuthProvider,
    request: OAuthLoginRequest,
    db: Session = Depends(get_session)
) -> Token:
    """Handle OAuth callback and return user token"""
    try:
        token = await oauth_service.handle_oauth_callback(
            provider=provider,
            code=request.code,
            db=db
        )
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "oauth_provider": current_user.oauth_provider,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.post("/logout")
async def logout():
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Token:
    """Refresh user token using current user"""
    # Create new token for the current user using centralized JWT service
    token = jwt_service.create_token(current_user)
    return token

@router.post("/refresh-token")
async def refresh_token_with_refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_session)
) -> Token:
    """Refresh access token using refresh token"""
    # Verify refresh token
    payload = jwt_service.verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user from database
    user_id = int(payload["sub"])
    stmt = select(User).where(User.id == user_id)
    user = db.exec(stmt).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    token = jwt_service.create_token(user)
    return token

# Legacy email login endpoint (for backward compatibility)
@router.post("/login/email")
async def email_login(email: str = Form(...)):
    """Legacy email login endpoint"""
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    return {"message": "Please use OAuth login instead", "email": email}
