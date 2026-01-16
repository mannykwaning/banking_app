"""
Authentication endpoints for user signup and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.services.auth_service import AuthService
from app.core.dependencies import get_auth_service, get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)

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
    logger.info(
        "Signup endpoint called",
        extra={"username": user_data.username, "email": user_data.email},
    )
    try:
        user = auth_service.register_user(user_data)
        logger.info(
            "User signup successful",
            extra={"user_id": user.id, "username": user.username},
        )
        return user
    except ValueError as e:
        logger.warning(
            "Signup failed", extra={"username": user_data.username, "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/signup/admin",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create admin user",
    description="Create a new superuser account. Requires ADMIN_SETUP_KEY for security.",
)
def signup_admin(
    user_data: UserCreate,
    admin_setup_key: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Register a new admin/superuser account.

    **Security:** Requires the ADMIN_SETUP_KEY from environment configuration.

    - **email**: Admin email address (must be unique)
    - **username**: Admin username (must be unique, 3-50 characters)
    - **password**: Admin password (minimum 8 characters)
    - **full_name**: Optional full name
    - **admin_setup_key**: Secret key from environment (ADMIN_SETUP_KEY)

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/signup/admin" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "admin@example.com",
        "username": "admin",
        "password": "adminpass123",
        "full_name": "System Admin"
      }' \
      -d '{"admin_setup_key": "your-secret-key"}'
    ```
    """
    from app.core.config import settings

    logger.info(
        "Admin signup endpoint called",
        extra={"username": user_data.username, "email": user_data.email},
    )

    # Verify admin setup key
    if admin_setup_key != settings.admin_setup_key:
        logger.warning(
            "Admin signup failed - invalid setup key",
            extra={"username": user_data.username},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin setup key",
        )

    try:
        user = auth_service.register_user(user_data, is_superuser=True)
        logger.info(
            "Admin user created successfully",
            extra={"user_id": user.id, "username": user.username},
        )
        return user
    except ValueError as e:
        logger.warning(
            "Admin signup failed",
            extra={"username": user_data.username, "error": str(e)},
        )
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
    logger.info("Login endpoint called", extra={"username": form_data.username})
    try:
        token = auth_service.login(form_data.username, form_data.password)
        logger.info("Login endpoint successful", extra={"username": form_data.username})
        return token
    except ValueError as e:
        logger.warning(
            "Login endpoint failed",
            extra={"username": form_data.username, "error": str(e)},
        )
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
    logger.debug(
        "Get current user info endpoint called",
        extra={"user_id": current_user.id, "username": current_user.username},
    )
    return current_user
