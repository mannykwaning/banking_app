# Admin User Quick Reference

Quick commands and examples for admin user management.

## Create Admin User

### Using API (Recommended)

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
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "is_superuser": true,
  "created_at": "2024-01-15T10:30:00"
}
```

### Using Database

```bash
# SQLite
sqlite3 data/banking_dev.db "UPDATE users SET is_superuser = 1 WHERE username = 'admin';"

# Python
python3 -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
user = db.query(User).filter(User.username == 'admin').first()
user.is_superuser = True
db.commit()
db.close()
"
```

## Login as Admin

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=SecureAdminPass123!"
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Access Admin Endpoints

```bash
# Store token
TOKEN="your-jwt-token-here"

# Get error summary
curl -X GET "http://localhost:8000/api/v1/admin/errors/summary" \
  -H "Authorization: Bearer $TOKEN"

# Get all errors
curl -X GET "http://localhost:8000/api/v1/admin/errors" \
  -H "Authorization: Bearer $TOKEN"

# Get recent errors (last 24h)
curl -X GET "http://localhost:8000/api/v1/admin/errors/recent" \
  -H "Authorization: Bearer $TOKEN"

# Get error details
curl -X GET "http://localhost:8000/api/v1/admin/errors/{error_id}" \
  -H "Authorization: Bearer $TOKEN"
```

## Check Admin Status

```bash
# SQLite
sqlite3 data/banking_dev.db "SELECT username, email, is_superuser FROM users;"

# Python
python3 -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f'{u.username:20} is_superuser={u.is_superuser}')
db.close()
"
```

## Generate Admin Setup Key

```bash
# For production - generate strong random key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# Xk9f_LmQp3rT8nV2jW7zY4sA1cD6eF0hG5iB3nM9uP2oR8tL4qJ
```

## Environment Variables

```bash
# .env.development
ADMIN_SETUP_KEY=dev-admin-setup-key-change-me-in-production

# .env.production (CHANGE THIS!)
ADMIN_SETUP_KEY=REPLACE-WITH-STRONG-ADMIN-KEY-AT-LEAST-32-CHARACTERS
```

## Test Admin Setup

```bash
# Run comprehensive test script
python test_admin_signup.py
```

## Common Issues

### "Invalid admin setup key"

```bash
# Check your .env file
cat .env.development | grep ADMIN_SETUP_KEY

# Make sure server loaded correct environment
echo $ENVIRONMENT  # Should be: development, test, or production
```

### "Admin privileges required" (403)

```bash
# Verify user is superuser
sqlite3 data/banking_dev.db "SELECT username, is_superuser FROM users WHERE username='admin';"

# If is_superuser=0, update it:
sqlite3 data/banking_dev.db "UPDATE users SET is_superuser = 1 WHERE username='admin';"
```

### "Email already registered"

```bash
# Use different email or login with existing account
# Or delete existing user first (not recommended for production)
sqlite3 data/banking_dev.db "DELETE FROM users WHERE email='admin@example.com';"
```

## Security Best Practices

1. **Generate strong admin setup key:**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Rotate key after creating admins:**
   - Update `ADMIN_SETUP_KEY` in `.env` file
   - Restart server

3. **Use strong admin passwords:**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols

4. **Monitor admin access:**

   ```bash
   grep "admin" logs/banking_app.log | grep -i "error\|warning"
   ```

5. **Limit admin accounts:**
   - Only create necessary admin users
   - Regularly audit admin list

## Full Workflow Example

```bash
# 1. Start server
python main.py

# 2. Create admin user
curl -X POST "http://localhost:8000/api/v1/auth/signup/admin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "AdminPass123!",
    "full_name": "Admin",
    "admin_setup_key": "dev-admin-setup-key-change-me-in-production"
  }'

# 3. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=AdminPass123!" | jq -r '.access_token')

# 4. Access admin endpoint
curl -X GET "http://localhost:8000/api/v1/admin/errors/summary" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

**See also:**

- [ADMIN_SETUP.md](ADMIN_SETUP.md) - Complete admin setup guide
- [AUTH_GUIDE.md](AUTH_GUIDE.md) - Authentication guide
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Error tracking guide
