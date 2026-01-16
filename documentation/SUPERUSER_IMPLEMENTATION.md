# Superuser Privilege Implementation Summary

## Overview

This document summarizes the implementation of the superuser (admin) privilege system in the Banking App API.

## Implementation Details

### 1. Database Model

**File:** `app/models/user.py`

```python
class User(Base):
    __tablename__ = "users"
    
    # ... other fields ...
    is_superuser = Column(Boolean, default=False, nullable=False)
```

- `is_superuser`: Boolean field indicating admin privileges
- Default: `False` (regular user)
- Used to control access to admin-only endpoints

### 2. Configuration

**Files:** `app/core/config.py`, `.env.{environment}`

Added `ADMIN_SETUP_KEY` configuration:

```python
# app/core/config.py
admin_setup_key: str = "change-me-in-production-admin-setup-key"
```

Environment files:

- `.env.development`: `ADMIN_SETUP_KEY=dev-admin-setup-key-change-me-in-production`
- `.env.production`: `ADMIN_SETUP_KEY=REPLACE-WITH-STRONG-ADMIN-KEY-AT-LEAST-32-CHARACTERS`
- `.env.test`: `ADMIN_SETUP_KEY=test-admin-setup-key-for-testing-only`

### 3. Repository Layer

**File:** `app/repositories/user_repository.py`

Updated `create()` method to support superuser creation:

```python
def create(self, user_data: UserCreate, hashed_password: str, is_superuser: bool = False) -> User:
    """Create a new user with optional superuser privileges."""
    user = User(
        # ... other fields ...
        is_superuser=is_superuser,  # Now configurable instead of hardcoded False
    )
    # ...
```

### 4. Service Layer

**File:** `app/services/auth_service.py`

Updated `register_user()` to support superuser creation:

```python
def register_user(self, user_data: UserCreate, is_superuser: bool = False) -> User:
    """Register a new user with optional superuser privileges."""
    # ...
    user = self.user_repository.create(user_data, hashed_password, is_superuser=is_superuser)
    # ...
```

### 5. API Endpoint

**File:** `app/api/v1/endpoints/auth.py`

Added new admin signup endpoint:

```python
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
    # Verify admin setup key
    if admin_setup_key != settings.admin_setup_key:
        raise HTTPException(status_code=403, detail="Invalid admin setup key")
    
    # Create superuser
    user = auth_service.register_user(user_data, is_superuser=True)
    return user
```

### 6. Authorization Dependency

**File:** `app/core/dependencies.py`

Existing dependency that checks superuser status:

```python
def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify user has admin privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
```

### 7. Protected Admin Endpoints

**File:** `app/api/v1/endpoints/admin_errors.py`

All admin endpoints use the `get_current_admin_user` dependency:

```python
@router.get("/errors", response_model=ErrorListResponse)
def get_errors(
    current_user: User = Depends(get_current_admin_user),  # Requires superuser
    # ...
):
    # Only accessible by superusers
```

## How It Works

### Creating an Admin User

1. **Obtain Admin Setup Key** from environment configuration (`.env.{environment}`)
2. **Call Admin Signup Endpoint:**

   ```bash
   POST /api/v1/auth/signup/admin
   {
     "email": "admin@example.com",
     "username": "admin",
     "password": "SecurePass123!",
     "full_name": "Admin User",
     "admin_setup_key": "your-secret-key"
   }
   ```

3. **Server validates:**
   - Admin setup key matches `ADMIN_SETUP_KEY` from config
   - User data is valid (unique email/username, strong password)
4. **Server creates user:**
   - Sets `is_superuser=True` in database
   - Returns user with superuser flag
5. **Admin can now access protected endpoints**

### Accessing Admin Endpoints

1. **Login as admin** to get JWT token
2. **Include token** in Authorization header: `Bearer <token>`
3. **Call admin endpoint** (e.g., `GET /api/v1/admin/errors/summary`)
4. **Server checks:**
   - Token is valid (authentication)
   - User has `is_superuser=True` (authorization)
   - Returns 403 if not superuser

### Security Flow

```
Regular User → Login → JWT Token → Admin Endpoint → 403 Forbidden ❌
Admin User   → Login → JWT Token → Admin Endpoint → 200 OK ✅
No Auth      → Admin Endpoint → 401 Unauthorized ❌
Wrong Key    → Admin Signup → 403 Forbidden ❌
```

## Security Features

### 1. Secret Key Protection

- Admin creation requires `ADMIN_SETUP_KEY` from environment
- Key should be strong, random, and kept secret
- Different keys for dev/test/prod environments

### 2. No Privilege Escalation

- Regular users cannot promote themselves
- Only the admin signup endpoint can create superusers
- Requires secret key that only admins know

### 3. Authentication + Authorization

- Two-layer security:
  1. Authentication: Valid JWT token required
  2. Authorization: `is_superuser=True` required for admin endpoints

### 4. Audit Trail

- All admin user creation logged:

  ```json
  {
    "timestamp": "2024-01-15 10:30:00",
    "level": "INFO",
    "message": "Admin user created successfully",
    "username": "admin",
    "user_id": "uuid-here"
  }
  ```

## Testing

### Test Script

Run `test_admin_signup.py` to verify:

1. ✅ Admin user creation with valid key
2. ✅ Invalid key rejection
3. ✅ Regular user cannot access admin endpoints
4. ✅ Admin can access admin endpoints

```bash
python test_admin_signup.py
```

### Manual Testing

1. **Create admin user:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/signup/admin" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@example.com",
       "username": "admin",
       "password": "AdminPass123!",
       "full_name": "Admin User",
       "admin_setup_key": "dev-admin-setup-key-change-me-in-production"
     }'
   ```

2. **Login:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=AdminPass123!"
   ```

3. **Access admin endpoint:**

   ```bash
   curl -X GET "http://localhost:8000/api/v1/admin/errors/summary" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

## Alternative Methods

### Method 1: API Endpoint (Implemented)

✅ Secure (requires secret key)  
✅ Scriptable/automatable  
✅ No direct database access needed  
⚠️ Key must be protected

### Method 2: Database Update

✅ Simple and direct  
⚠️ Requires database access  
⚠️ Manual process  
❌ Not scriptable

```sql
UPDATE users SET is_superuser = 1 WHERE username = 'admin';
```

### Method 3: CLI Tool (Future)

✅ User-friendly  
✅ Can add additional checks  
⚠️ Requires implementation

## Production Recommendations

1. **Generate Strong Keys:**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Rotate Keys After Use:**
   - Change `ADMIN_SETUP_KEY` after creating admin users
   - Consider one-time use keys

3. **Disable Admin Signup (Optional):**
   - After initial setup, comment out the endpoint
   - Or add check to prevent creation if admins exist:

     ```python
     if db.query(User).filter(User.is_superuser == True).count() > 0:
         raise HTTPException(403, "Admin users already exist")
     ```

4. **Monitor Admin Activity:**

   ```bash
   grep "admin" logs/banking_app.log
   ```

5. **Limit Admin Accounts:**
   - Create only necessary admin accounts
   - Use strong, unique passwords
   - Regular audit of admin users

## Troubleshooting

### "Invalid admin setup key"

**Problem:** Key mismatch  
**Solution:** Check `.env.{environment}` file, ensure correct environment loaded

### "Admin privileges required"

**Problem:** User is not superuser  
**Solution:** Verify in database:

```sql
SELECT username, is_superuser FROM users WHERE username='admin';
```

### "Email already registered"

**Problem:** Admin user already exists  
**Solution:** Use existing admin or create with different email

## Related Files

- **Documentation:**
  - [ADMIN_SETUP.md](ADMIN_SETUP.md) - Complete admin setup guide
  - [AUTH_GUIDE.md](AUTH_GUIDE.md) - Authentication guide
  - [ERROR_HANDLING.md](ERROR_HANDLING.md) - Error tracking guide

- **Code:**
  - [app/models/user.py](../app/models/user.py) - User model with is_superuser
  - [app/api/v1/endpoints/auth.py](../app/api/v1/endpoints/auth.py) - Admin signup endpoint
  - [app/core/dependencies.py](../app/core/dependencies.py) - Admin authorization
  - [app/api/v1/endpoints/admin_errors.py](../app/api/v1/endpoints/admin_errors.py) - Admin endpoints

- **Testing:**
  - [test_admin_signup.py](../test_admin_signup.py) - Admin creation test script

## Summary

The superuser privilege system provides secure, scriptable admin user creation with:

- ✅ Secret key protection
- ✅ Clean API design
- ✅ Proper authentication and authorization
- ✅ Comprehensive documentation
- ✅ Test coverage

Regular users default to `is_superuser=False` and cannot access admin endpoints. Admin users created via `/api/v1/auth/signup/admin` with the secret `ADMIN_SETUP_KEY` get `is_superuser=True` and full access to admin error monitoring endpoints.
