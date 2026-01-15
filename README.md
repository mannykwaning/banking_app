# Banking App API

A production-ready banking application backend API built with FastAPI and SQLite, featuring OAuth2 authentication, Docker support, and comprehensive testing.

## Features

- 🚀 FastAPI framework with automatic OpenAPI documentation
- 🔐 OAuth2 authentication with JWT tokens
- 🔒 Secure password hashing with bcrypt
- 💾 SQLite database with SQLAlchemy ORM
- 🐳 Docker and Docker Compose support
- 🌍 Environment variable configuration (.env support)
- 📝 Interactive API documentation with Swagger UI (OAuth2 integrated)
- ✅ Banking operations (accounts and transactions)
- 🧪 Comprehensive unit and integration tests
- 🏗️ Clean architecture with repository and service layer patterns

## Prerequisites

- Python 3.11+ (for local development)
- Docker and Docker Compose (for containerized deployment)

## Project Structure

```plaintext
banking_app_backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── accounts.py      # Account endpoints
│   │           ├── auth.py          # Authentication endpoints
│   │           └── transactions.py  # Transaction endpoints
│   ├── core/
│   │   ├── config.py               # Configuration and settings
│   │   ├── database.py             # Database setup
│   │   └── dependencies.py         # FastAPI dependencies
│   ├── models/
│   │   ├── account.py              # Account database model
│   │   ├── transaction.py          # Transaction database model
│   │   └── user.py                 # User database model
│   ├── repositories/
│   │   ├── account_repository.py   # Account data access
│   │   ├── transaction_repository.py
│   │   └── user_repository.py      # User data access
│   ├── schemas/
│   │   ├── account.py              # Account request/response schemas
│   │   ├── transaction.py          # Transaction schemas
│   │   └── user.py                 # User and auth schemas
│   └── services/
│       ├── account_service.py      # Account business logic
│       ├── auth_service.py         # Authentication service
│       └── transaction_service.py  # Transaction business logic
├── tests/
│   ├── unit/                       # Unit tests
│   │   ├── test_auth_service.py
│   │   ├── test_user_repository.py
│   │   └── ...
│   └── integration/                # Integration tests
│       ├── conftest.py
│       ├── test_auth.py
│       └── ...
├── data/                           # SQLite database files
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── AUTH_GUIDE.md                   # Authentication usage guide
├── .env.example                    # Environment template
└── README.md                       # This file
```

## Quick Start

### Option 1: Using Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/mannykwaning/banking_app.git
   cd banking_app
   ```

2. **Create environment file**

   ```bash
   cp .env.example .env
   # Edit .env if needed to customize configuration
   ```

3. **Build and run with Docker Compose**

   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   - API: <http://localhost:8000>
   - Swagger UI: <http://localhost:8000/docs>
   - ReDoc: <http://localhost:8000/redoc>

### Option 2: Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/mannykwaning/banking_app.git
   cd banking_app
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**

   ```bash
   cp .env.example .env
   ```

5. **Run the application**

   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - API: <http://localhost:8000>
   - Swagger UI: <http://localhost:8000/docs>
   - ReDoc: <http://localhost:8000/redoc>

## API Endpoints

### Root & Health (Public)

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Authentication (Public)

- `POST /api/v1/auth/signup` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token (OAuth2 flow)
- `POST /api/v1/auth/login/json` - Login with JSON body
- `GET /api/v1/auth/me` - Get current user information (requires authentication)

### Accounts (Protected - Requires Authentication)

- `POST /api/v1/accounts` - Create a new bank account
- `GET /api/v1/accounts` - List all accounts
- `GET /api/v1/accounts/{account_id}` - Get account details with transactions
- `DELETE /api/v1/accounts/{account_id}` - Delete an account

### Transactions (Protected - Requires Authentication)

- `POST /api/v1/transactions` - Create a new transaction (deposit/withdrawal)
- `GET /api/v1/transactions` - List all transactions
- `GET /api/v1/transactions/{transaction_id}` - Get transaction details

## Example Usage

### Authentication Flow

#### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

#### 2. Login to Get Access Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepass123"
  }'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Protected Endpoints

**Note:** All account and transaction endpoints require authentication. Include the token in the Authorization header.

#### Create an Account

```bash
curl -X POST "http://localhost:8000/api/v1/accounts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "account_holder": "John Doe",
    "account_type": "checking",
    "initial_balance": 1000.0
  }'
```

#### Make a Deposit

```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "account_id": 1,
    "transaction_type": "deposit",
    "amount": 500.0,
    "description": "Salary deposit"
  }'
```

#### Make a Withdrawal

```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "account_id": 1,
    "transaction_type": "withdrawal",
    "amount": 200.0,
    "description": "ATM withdrawal"
  }'
```

#### Get Account Details

```bash
curl "http://localhost:8000/api/v1/accounts/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" button (🔓 icon at the top)
3. Login at `/api/v1/auth/login` to get your token
4. Enter the token in the authorization dialog
5. All protected endpoints will now work with your credentials

For detailed authentication examples and troubleshooting, see [AUTH_GUIDE.md](AUTH_GUIDE.md).

## Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```env
# Database Configuration
DATABASE_URL=sqlite:///./data/banking.db

# Application Configuration
APP_NAME=Banking App API
APP_VERSION=1.0.0
DEBUG=True

# API Configuration
API_V1_PREFIX=/api/v1

# Security (IMPORTANT: Change in production!)
SECRET_KEY=your-secret-key-here-change-in-production
```

**Security Note:** The `SECRET_KEY` is used to sign JWT tokens. In production:

- Use a strong, randomly generated key (at least 32 characters)
- Never commit real secrets to version controlis automatically created in the `data/` directory when you first run the application.

### Models

- **User**: User accounts with authentication credentials (email, username, hashed password)
- **Account**: Bank accounts with account number, holder name, type, and balance
- **Transaction**: Financial transactions (deposits/withdrawals) linked to accounts

### Database Schema

All database models inherit from SQLAlchemy's declarative base and include:

- Automatic table creation on startup
- Timestamps (created_at, updated_at) where applicable
- Proper indexes for performance
- Foreign key relationshipsabase file (`banking.db`) is automatically created when you first run the application.

## Development

### Running Tests

```bash
# Run all tests (unit + integration)
pytest -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Authentication tests
pytest tests/unit/test_auth_service.py tests/unit/test_user_repository.py -v
pytest tests/integration/test_auth.py -v

# With coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html to view coverage

# Run tests with output
pytest -v -s
```

### Test Structure

The test suite includes:

- **Unit Tests**: Test individual components in isolation (services, repositories)
- **Integration Tests**: Test API endpoints end-to-end with database
- **Fixtures**: Reusable test setup in `conftest.py` files
- **Coverage**: Comprehensive test coverage of all major functionality

### Code Formatting

```bash
# Install formatting tools
pip install black ruff

# Format code
black .

# Lint code
ruff check .
```

## Docker Commands

```bash
# Build the image
docker-compose build

# Start services

# Remove volumes (clears database)
docker-compose down -v
```

## Security Best Practices

- ✅ Passwords are hashed using bcrypt (never stored in plain text)
- ✅ JWT tokens expire after 30 minutes
- ✅ OAuth2 password bearer flow for secure authentication
- ✅ Email validation on registration
- ✅ Password minimum length enforcement (8 characters)
- ⚠️ **Production**: Use HTTPS to protect tokens in transit
- ⚠️ **Production**: Change the default `SECRET_KEY` to a strong random value
- ⚠️ **Production**: Use a production-grade database (PostgreSQL, MySQL)
- ⚠️ **Production**: Implement rate limiting on authentication endpointsker-compose up

### Start in detached mode

docker-compose up -d

### View logs

docker-compose logs -f

### Stop services

docker-compose down

### Rebuild and restart

docker-compose up --build

```plaintext

## Architecture

This project follows clean architecture principles with clear separation of concerns:

- **API Layer** (`api/v1/endpoints/`): HTTP request/response handling
- **Service Layer** (`services/`): Business logic and orchestration
- **Repository Layer** (`repositories/`): Data access and persistence
- **Models** (`models/`): SQLAlchemy database models
- **Schemas** (`schemas/`): Pydantic models for validation and serialization
- **Core** (`core/`): Configuration, database setup, and dependencies

## Additional Documentation

- **[AUTH_GUIDE.md](AUTH_GUIDE.md)** - Comprehensive authentication guide with examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design decisions
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project structure
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Database migration guide

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions, please open an issue on the GitHub repository.

## Roadmap

Future enhancements planned:
- [ ] Password reset functionality
- [ ] Email verification
- [ ] Refresh token support
- [ ] Role-based access control (RBAC)
- [ ] Account lockout after failed login attempts
- [ ] OAuth2 social login (Google, GitHub)
- [ ] API rate limiting
- [ ] Logging and monitoring
- [ ] Database migrations with Alembic
- [ ] CI/CD pipeline
