"""
Authentication endpoints for user signup and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.services.auth_service import AuthService
from app.core.dependencies import get_auth_service, get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Register a new user account.

    - **email**: User's email address (must be unique)
    - **username**: Username (must be unique, 3-50 characters)
    - **password**: Password (minimum 8 characters)
    - **full_name**: Optional full name
    """
    try:
        user = auth_service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Login and get access token.

    Use this endpoint with OAuth2 password flow for Swagger UI integration.

    - **username**: Your username
    - **password**: Your password

    Returns a bearer token for authentication.
    """
    try:
        token = auth_service.login(form_data.username, form_data.password)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login/json", response_model=Token)
def login_json(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Login with JSON body (alternative to form data).

    - **username**: Your username
    - **password**: Your password

    Returns a bearer token for authentication.
    """
    try:
        token = auth_service.login(login_data.username, login_data.password)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user information.

    Requires authentication (Bearer token).
    """
    return current_user
