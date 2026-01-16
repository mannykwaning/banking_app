# Authentication System - Usage Guide

## Overview

The Banking App API now includes OAuth2-based authentication with JWT tokens. All API endpoints (except signup and login) now require authentication.

## Features

- ✅ User registration (signup)
- ✅ Login with JWT bearer tokens
- ✅ Password hashing with bcrypt
- ✅ Protected API endpoints
- ✅ Token-based authentication
- ✅ FastAPI Swagger UI integration
- ✅ Unit and integration tests

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access Swagger UI

Open your browser and navigate to:

```plaintext
http://localhost:8000/docs
```

## Using Authentication in Swagger UI

### Step 1: Register a New User

1. Navigate to the `/api/v1/auth/signup` endpoint in Swagger UI
2. Click "Try it out"
3. Enter user details:

   ```json
   {
     "email": "user@example.com",
     "username": "johndoe",
     "password": "securepassword123",
     "full_name": "John Doe"
   }
   ```

4. Click "Execute"

### Step 2: Login and Get Token

1. Navigate to the `/api/v1/auth/login` endpoint
2. Click "Try it out"
3. Enter credentials:
   - **username**: johndoe
   - **password**: securepassword123
4. Click "Execute"
5. Copy the `access_token` from the response

### Step 3: Authorize in Swagger UI

1. Click the "Authorize" button at the top of the Swagger UI page (🔓 icon)
2. In the popup, enter the token in the format: `Bearer <your_token_here>`
   - Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Click "Authorize"
4. Click "Close"

### Step 4: Use Protected Endpoints

Now you can use any protected endpoint (accounts, transactions, etc.):

1. Navigate to any endpoint (e.g., `/api/v1/accounts`)
2. Click "Try it out"
3. Fill in the required parameters
4. Click "Execute"

The authorization header will be automatically included in all requests.

## API Endpoints

### Authentication Endpoints

- **POST `/api/v1/auth/signup`** - Register a new user
  - Request body: `UserCreate` (email, username, password, full_name)
  - Response: `UserResponse` (user details without password)

- **POST `/api/v1/auth/login`** - Login (OAuth2 password flow)
  - Form data: username, password
  - Response: `Token` (access_token, token_type)

- **POST `/api/v1/auth/login/json`** - Login with JSON body (alternative)
  - Request body: `LoginRequest` (username, password)
  - Response: `Token` (access_token, token_type)

- **GET `/api/v1/auth/me`** - Get current user information (protected)
  - Requires: Bearer token
  - Response: `UserResponse` (current user details)

### Protected Endpoints

All account and transaction endpoints now require authentication:

- `/api/v1/accounts/*` - All account operations
- `/api/v1/transactions/*` - All transaction operations

## Using the API Programmatically

### Python Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# 1. Sign up
signup_data = {
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "full_name": "John Doe"
}
response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
print(f"Signup: {response.status_code}")

# 2. Login
login_data = {
    "username": "johndoe",
    "password": "securepassword123"
}
response = requests.post(f"{BASE_URL}/auth/login/json", json=login_data)
token = response.json()["access_token"]
print(f"Token: {token}")

# 3. Use authenticated endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/accounts", headers=headers)
print(f"Accounts: {response.json()}")

# 4. Create an account
account_data = {
    "account_holder": "John Doe",
    "account_type": "checking",
    "initial_balance": 1000.0
}
response = requests.post(f"{BASE_URL}/accounts", json=account_data, headers=headers)
print(f"New account: {response.json()}")
```

### CURL Examples

```bash
# Sign up
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'

# Use authenticated endpoint (replace TOKEN with actual token)
curl -X GET "http://localhost:8000/api/v1/accounts" \
  -H "Authorization: Bearer TOKEN"
```

## Configuration

### JWT Settings

You can configure JWT settings in `app/core/config.py`:

- **secret_key**: Used to sign JWT tokens (automatically generated if not set)
- **Access token expiration**: Currently set to 30 minutes in `app/services/auth_service.py`

To set a custom secret key, create a `.env` file:

```env
SECRET_KEY=your-super-secret-key-here
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run Integration Tests Only

```bash
pytest tests/integration/
```

### Run Authentication Tests

```bash
pytest tests/unit/test_auth_service.py tests/unit/test_user_repository.py
pytest tests/integration/test_auth.py
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
```

## Security Notes

1. **Password Requirements**: Minimum 8 characters
2. **Token Expiration**: Access tokens expire after 30 minutes
3. **Password Hashing**: Uses bcrypt with automatic salt generation
4. **HTTPS**: In production, always use HTTPS to protect tokens in transit
5. **Secret Key**: Use a strong, randomly generated secret key in production

## Troubleshooting

### "Could not validate credentials" Error

- Ensure your token is not expired (tokens are valid for 30 minutes)
- Check that you're including the full "Bearer " prefix in the Authorization header
- Make sure you're using the token from the most recent login

### "Email already registered" or "Username already taken"

- Use a different email address or username
- These must be unique across all users

### Database Issues

If you encounter database-related errors, you may need to recreate the database:

```bash
rm data/banking.db  # Remove old database
python main.py      # Restart server to create new database
```

## Project Structure

```plaintext
app/
├── models/
│   └── user.py              # User database model
├── schemas/
│   └── user.py              # User request/response schemas
├── repositories/
│   └── user_repository.py   # User database operations
├── services/
│   └── auth_service.py      # Authentication logic (password hashing, JWT)
├── api/v1/endpoints/
│   └── auth.py              # Authentication endpoints
└── core/
    └── dependencies.py      # Auth dependencies (get_current_user)

tests/
├── unit/
│   ├── test_auth_service.py        # Unit tests for auth service
│   └── test_user_repository.py     # Unit tests for user repository
└── integration/
    └── test_auth.py                 # Integration tests for auth endpoints
```

## Next Steps

- Implement password reset functionality
- Add email verification
- Implement refresh tokens for long-lived sessions
- Add role-based access control (RBAC)
- Implement account lockout after failed login attempts
- Add OAuth2 social login (Google, GitHub, etc.)
