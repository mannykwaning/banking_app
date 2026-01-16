# Admin User Setup Guide

This guide explains how to create and manage superuser (admin) accounts in the Banking App API.

## Table of Contents

- [Overview](#overview)
- [Creating Your First Admin User](#creating-your-first-admin-user)
- [Admin Setup Methods](#admin-setup-methods)
- [Security Considerations](#security-considerations)
- [Admin Privileges](#admin-privileges)

---

## Overview

Admin users (superusers) have elevated privileges to:

- Access error monitoring endpoints (`/api/v1/admin/errors/*`)
- View system-wide error logs and analytics
- Monitor application health and issues

Regular users **cannot** access admin endpoints. The `is_superuser` flag in the User model determines admin status.

---

## Creating Your First Admin User

### Method 1: Admin Signup Endpoint (Recommended)

Use the special admin signup endpoint with the `ADMIN_SETUP_KEY` from your environment configuration.

#### Step 1: Get Your Admin Setup Key

Check your `.env.{environment}` file for the `ADMIN_SETUP_KEY`:

```bash
# .env.development
ADMIN_SETUP_KEY=dev-admin-setup-key-change-me-in-production
```

**Production:** Generate a strong random key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 2: Call the Admin Signup Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup/admin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "SecureAdminPass123!",
    "full_name": "System Administrator",
    "admin_setup_key": "dev-admin-setup-key-change-me-in-production"
  }'
```

**Response:**

```json
{
  "id": "uuid-here",
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "System Administrator",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

### Method 2: Direct Database Update

If you already have a user account, promote it to admin via database:

#### Using SQLite CLI

```bash
sqlite3 data/banking_dev.db "UPDATE users SET is_superuser = 1 WHERE username = 'myuser';"
```

#### Using Python Script

```python
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "myuser").first()
if user:
    user.is_superuser = True
    db.commit()
    print(f"User '{user.username}' is now a superuser")
else:
    print("User not found")
db.close()
```

---

### Method 3: CLI Script (Future Enhancement)

*Coming soon: A dedicated CLI tool for admin management*

---

## Admin Setup Methods Comparison

| Method | Security | Ease of Use | Best For |
|--------|----------|-------------|----------|
| **Admin Signup Endpoint** | ⭐⭐⭐ Requires secret key | ⭐⭐⭐ Very easy | Initial setup, automated deployments |
| **Database Update** | ⭐⭐ Requires DB access | ⭐⭐ Moderate | Existing users, emergency access |
| **CLI Script** | ⭐⭐⭐ Requires server access | ⭐⭐⭐ Very easy | *Future feature* |

---

## Security Considerations

### 1. Protect Your Admin Setup Key

❌ **Never commit the real key to version control**

```bash
# Bad - using default key in production
ADMIN_SETUP_KEY=dev-admin-setup-key-change-me-in-production
```

✅ **Use a strong, unique key in production**

```bash
# Good - generated random key
ADMIN_SETUP_KEY=Xk9f_LmQp3rT8nV2jW7zY4sA1cD6eF0hG5iB3nM9uP2oR8tL4qJ
```

### 2. Disable Admin Signup After Setup

For production, consider disabling the admin signup endpoint after creating your initial admin user:

```python
# In app/api/v1/endpoints/auth.py
# Comment out or remove the @router.post("/signup/admin") endpoint
```

Or add additional checks:

```python
# Only allow admin creation if no admins exist
admin_count = db.query(User).filter(User.is_superuser == True).count()
if admin_count > 0:
    raise HTTPException(status_code=403, detail="Admin users already exist")
```

### 3. Rotate Admin Setup Key

Change your `ADMIN_SETUP_KEY` periodically and after each admin user creation:

```bash
# Generate new key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env file
ADMIN_SETUP_KEY=new_generated_key_here
```

### 4. Audit Admin Access

Monitor admin API usage:

```bash
# Check error logs for admin endpoint access
grep "admin_errors" logs/banking_app.log
```

---

## Admin Privileges

### Endpoints Requiring Admin Access

All endpoints under `/api/v1/admin/` require `is_superuser=True`:

1. **GET /api/v1/admin/errors** - List all errors
2. **GET /api/v1/admin/errors/summary** - Error analytics
3. **GET /api/v1/admin/errors/recent** - Recent errors (last 24h)
4. **GET /api/v1/admin/errors/{error_id}** - Error details

### How Admin Check Works

```python
# app/core/dependencies.py
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

### Testing Admin Access

1. Create admin user (using method above)
2. Login to get JWT token:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=SecureAdminPass123!"
   ```

3. Use token to access admin endpoints:

   ```bash
   curl -X GET "http://localhost:8000/api/v1/admin/errors/summary" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

---

## Troubleshooting

### "Invalid admin setup key" Error

**Cause:** The `admin_setup_key` parameter doesn't match `ADMIN_SETUP_KEY` in your environment.

**Solution:**

1. Check your `.env.{environment}` file
2. Ensure you're using the correct environment (dev/test/prod)
3. Restart the server after changing environment variables

### "Admin privileges required" Error

**Cause:** User is not a superuser (`is_superuser=False`).

**Solution:**

1. Verify user's superuser status:

   ```bash
   sqlite3 data/banking_dev.db "SELECT username, is_superuser FROM users WHERE username='admin';"
   ```

2. If `is_superuser=0`, promote the user using Method 2 (Database Update)

### Can't Create More Admin Users

If you disabled the admin signup endpoint after initial setup, you'll need to use the database update method (Method 2) to create additional admins.

---

## Best Practices

1. **Create one admin user initially** - Use admin signup endpoint
2. **Rotate the admin setup key** - After creating admin user
3. **Use strong passwords** - For admin accounts (min 12+ chars, mixed case, symbols)
4. **Limit admin accounts** - Only create what's necessary
5. **Audit regularly** - Review admin access logs
6. **Separate credentials** - Don't use admin accounts for regular operations

---

## Related Documentation

- [Authentication Guide](AUTH_GUIDE.md) - User authentication and JWT tokens
- [Error Handling Guide](ERROR_HANDLING.md) - Error tracking system details
- [Environment Guide](ENVIRONMENT_GUIDE.md) - Environment configuration

---

**Security Note:** Admin users have full access to error logs which may contain sensitive information. Protect admin credentials carefully and follow the principle of least privilege.
