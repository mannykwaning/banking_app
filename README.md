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
- 📊 **Account statements with balance and activity tracking**
  - Generate detailed account statements
  - Customizable date ranges for statement periods
  - Transaction summaries by type (deposits, withdrawals, transfers)
  - Current balance and transaction count
- � **Card Management with Encryption**
  - Issue debit, credit, and prepaid cards
  - Encrypted storage of PAN (Primary Account Number) and CVV
  - Support for multiple cards per account (up to 5 active)
  - Card status management (active, inactive, blocked, expired)
  - Secure card detail retrieval with masking
- �💸 **Secure money transfers with ACID compliance**
  - Internal transfers (between accounts in the system)
  - External transfers (to other banks)
  - Transaction limits and validation
  - Automatic rollback on failure
- 🧪 Comprehensive unit and integration tests
- 🏗️ Clean architecture with repository and service layer patterns
- 📊 Structured JSON logging with configurable log levels and output
- 🚨 **Comprehensive error tracking and reporting**
  - Automatic error categorization (validation, auth, server, database)
  - PII sanitization in error logs
  - Error storage in database for analysis
  - Admin API for error monitoring and reporting
  - Proper HTTP status codes for all error types

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
│   │           ├── cards.py         # Card endpoints (NEW)
│   │           ├── transactions.py  # Transaction endpoints
│   │           └── transfers.py     # Transfer endpoints
│   ├── core/
│   │   ├── config.py               # Configuration and settings
│   │   ├── database.py             # Database setup
│   │   ├── dependencies.py         # FastAPI dependencies
│   │   └── encryption.py           # Encryption utilities
│   ├── models/
│   │   ├── account.py              # Account database model
│   │   ├── card.py                 # Card database model
│   │   ├── transaction.py          # Transaction database model
│   │   └── user.py                 # User database model
│   ├── repositories/
│   │   ├── account_repository.py   # Account data access
│   │   ├── card_repository.py      # Card data access
│   │   ├── transaction_repository.py
│   │   └── user_repository.py      # User data access
│   ├── schemas/
│   │   ├── account.py              # Account schemas (includes AccountStatementResponse)
│   │   ├── card.py                 # Card schemas
│   │   ├── transaction.py          # Transaction schemas
│   │   └── user.py                 # User and auth schemas
│   └── services/
│       ├── account_service.py      # Account business logic
│       ├── auth_service.py         # Authentication service
│       ├── card_service.py         # Card service with encryption
│       ├── transaction_service.py  # Transaction business logic
│       └── transfer_service.py     # Transfer service with ACID compliance
├── tests/
│   ├── unit/                       # Unit tests
│   │   ├── test_auth_service.py
│   │   ├── test_user_repository.py
│   │   └── ...
│   └── integration/                # Integration tests
│       ├── conftest.py
│       ├── test_auth.py
│       └── ...
├── documentation/                  # All documentation files
│   ├── ARCHITECTURE.md             # System architecture
│   ├── AUTH_GUIDE.md               # Authentication guide
│   ├── CARDS_GUIDE.md              # Card management guide
│   ├── ENVIRONMENT_GUIDE.md        # Environment configuration
│   ├── ENVIRONMENT_QUICKREF.md     # Environment quick reference
│   ├── LOGGING_GUIDE.md            # Logging guide
│   ├── MIGRATION_GUIDE.md          # Database migration guide
│   ├── PROJECT_REQUIREMENTS.md     # Project requirements
│   ├── PROJECT_STRUCTURE.md        # Detailed project structure
│   ├── TRANSFER_GUIDE.md           # Transfer guide
│   ├── TRANSFER_IMPLEMENTATION.md  # Transfer implementation
│   ├── TRANSFER_MIGRATION.md       # Transfer migration guide
│   ├── TRANSFER_QUICKREF.md        # Transfer quick reference
│   └── TRANSFER_README.md          # Transfer quick start
├── data/                           # SQLite database files
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── .env.example                    # Environment template
└── README.md                       # This file
```

## Quick Start

### Option 1: Using Docker (Recommended)

#### Development Environment

1. **Clone the repository**

   ```bash
   git clone https://github.com/mannykwaning/banking_app.git
   cd banking_app
   ```

2. **Start development environment**

   ```bash
   # Uses .env.development configuration
   docker-compose -f docker-compose.dev.yml up --build
   ```

   **Note:** If you've run the app before and are adding transfer features, the database will be **automatically recreated** with the new schema. No manual migration needed for SQLite!

3. **Access the API**
   - API: <http://localhost:8000>
   - Swagger UI: <http://localhost:8000/docs>
   - ReDoc: <http://localhost:8000/redoc>

#### Production Environment

1. **Configure production settings**

   ```bash
   # Update .env.production with your settings
   # IMPORTANT: Set a strong SECRET_KEY
   ```

2. **Run production container**

   ```bash
   docker-compose up --build
   ```

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

4. **Set environment for development**

   ```bash
   # Option 1: Export environment variable
   export ENVIRONMENT=development
   
   # Option 2: Or create a .env file (will use .env.development by default)
   cp .env.development .env
   ```

5. **Prepare the database**

   ```bash
   # For a fresh start (recommended for testing transfers):
   rm -f data/banking.db  # Removes old database if exists
   
   # SQLAlchemy will automatically create the database with the correct schema
   # on first run - no manual migration needed!
   ```

6. **Run the application**

   ```bash
   # With ENVIRONMENT variable
   ENVIRONMENT=development uvicorn main:app --reload
   
   # Or if you copied .env file
   uvicorn main:app --reload
   ```

7. **Access the API**
   - API: <http://localhost:8000>
   - Swagger UI: <http://localhost:8000/docs>
   - ReDoc: <http://localhost:8000/redoc>

## Environment Configuration

The application supports three environments: **development**, **test**, and **production**.

### Quick Setup

```bash
# Development (verbose logging, debug enabled)
ENVIRONMENT=development uvicorn main:app --reload

# Test (minimal logging, in-memory DB)
ENVIRONMENT=test pytest

# Production (optimized, secure settings)
ENVIRONMENT=production uvicorn main:app --host 0.0.0.0 --port 8000
```

Each environment has its own configuration file:

- `.env.development` - Development settings
- `.env.test` - Test settings  
- `.env.production` - Production settings (update SECRET_KEY!)

For detailed information, see [ENVIRONMENT_GUIDE.md](documentation/ENVIRONMENT_GUIDE.md).

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
- `GET /api/v1/accounts/{account_id}/statement` - Generate account statement with balance and activity 📊
- `DELETE /api/v1/accounts/{account_id}` - Delete an account

### Transactions (Protected - Requires Authentication)

- `POST /api/v1/transactions` - Create a new transaction (deposit/withdrawal)
- `GET /api/v1/transactions` - List all transactions
- `GET /api/v1/transactions/{transaction_id}` - Get transaction details

### Transfers (Protected - Requires Authentication) 💸

- `POST /api/v1/transfers/internal` - Create an internal transfer between accounts
- `POST /api/v1/transfers/external` - Create an external transfer to another bank
- `GET /api/v1/transfers/{reference_id}` - Get transfer details and status

> **📖 For detailed transfer documentation, see [TRANSFER_README.md](documentation/TRANSFER_README.md)**

### Cards (Protected - Requires Authentication) 💳

- `POST /api/v1/cards` - Issue a new card for an account
- `GET /api/v1/cards` - List all cards
- `GET /api/v1/cards/{card_id}` - Get card details (without sensitive data)
- `GET /api/v1/cards/{card_id}/details` - Get full card details including PAN and CVV
- `GET /api/v1/cards/{card_id}/masked` - Get masked card number
- `GET /api/v1/cards/account/{account_id}` - Get all cards for an account
- `PATCH /api/v1/cards/{card_id}/status` - Update card status
- `POST /api/v1/cards/{card_id}/block` - Block a card
- `POST /api/v1/cards/{card_id}/activate` - Activate a card

> **📖 For detailed card documentation, see [CARDS_GUIDE.md](documentation/CARDS_GUIDE.md)**

### Admin - Error Tracking (Protected - Requires Admin/Superuser) 🚨

- `GET /api/v1/admin/errors` - List error logs with filtering and pagination
- `GET /api/v1/admin/errors/summary` - Get error statistics and summaries
- `GET /api/v1/admin/errors/recent` - Get most recent errors
- `GET /api/v1/admin/errors/{error_id}` - Get detailed error information with stack trace

**Authentication:** Requires JWT token **AND** superuser privileges (`is_superuser=True`)

> **📖 For detailed error tracking documentation, see [ERROR_HANDLING.md](documentation/ERROR_HANDLING.md)**

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
    "description": "Initial deposit"
  }'
```

#### Issue a Card 💳

```bash
curl -X POST "http://localhost:8000/api/v1/cards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "account_id": 1,
    "cardholder_name": "JOHN DOE",
    "card_type": "debit"
  }'
```

Response:

```json
{
  "id": 1,
  "account_id": 1,
  "card_number_last4": "1234",
  "cardholder_name": "JOHN DOE",
  "card_type": "debit",
  "status": "active",
  "expiry_month": 12,
  "expiry_year": 2029,
  "issued_at": "2026-01-15T10:30:00",
  "created_at": "2026-01-15T10:30:00",
  "updated_at": "2026-01-15T10:30:00"
}
```

#### Get Card Details (Sensitive Data)

```bash
curl -X GET "http://localhost:8000/api/v1/cards/1/details" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response includes decrypted PAN and CVV:

```json
{
  "id": 1,
  "account_id": 1,
  "card_number_last4": "1234",
  "cardholder_name": "JOHN DOE",
  "card_type": "debit",
  "status": "active",
  "expiry_month": 12,
  "expiry_year": 2029,
  "card_number": "4000000000001234",
  "cvv": "123",
  "issued_at": "2026-01-15T10:30:00",
  "created_at": "2026-01-15T10:30:00",
  "updated_at": "2026-01-15T10:30:00"
}
```

#### Block a Card

```bash
curl -X POST "http://localhost:8000/api/v1/cards/1/block" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
``` \
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

### Money Transfers 💸

#### Create Internal Transfer

Transfer money between two accounts within the system:

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/internal" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "source_account_id": 1,
    "destination_account_id": 2,
    "amount": 100.00,
    "description": "Payment for services"
  }'
```

#### Create External Transfer

Transfer money to an external bank account:

```bash
curl -X POST "http://localhost:8000/api/v1/transfers/external" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "source_account_id": 1,
    "external_account_number": "9876543210",
    "external_bank_name": "Other Bank",
    "external_routing_number": "123456789",
    "amount": 500.00,
    "description": "Payment to vendor"
  }'
```

#### Check Transfer Status

```bash
curl "http://localhost:8000/api/v1/transfers/TXN-A1B2C3D4E5F6" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Transfer Features:**

- ✅ ACID compliance with automatic rollback
- ✅ Balance validation and transaction limits
- ✅ Daily transfer limits enforcement
- ✅ Internal transfers (instant completion)
- ✅ External transfers (pending status)
- ✅ Comprehensive audit logging

### Account Statements 📊

Generate detailed account statements with balance and transaction activity.

#### Generate Statement (Default: Last 30 Days)

```bash
curl "http://localhost:8000/api/v1/accounts/1/statement" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Generate Statement with Custom Date Range

```bash
curl "http://localhost:8000/api/v1/accounts/1/statement?start_date=2026-01-01T00:00:00&end_date=2026-01-15T23:59:59" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:

```json
{
  "account_id": 1,
  "account_number": "1234567890",
  "account_holder": "John Doe",
  "account_type": "checking",
  "current_balance": 1800.0,
  "statement_period": {
    "start_date": "2025-12-16T00:00:00",
    "end_date": "2026-01-15T23:59:59"
  },
  "total_deposits": 1500.0,
  "total_withdrawals": 200.0,
  "total_transfers_in": 600.0,
  "total_transfers_out": 100.0,
  "transaction_count": 8,
  "transactions": [
    {
      "id": 1,
      "account_id": 1,
      "transaction_type": "deposit",
      "amount": 500.0,
      "description": "Salary deposit",
      "status": "completed",
      "created_at": "2026-01-10T10:00:00"
    },
    {
      "id": 2,
      "account_id": 1,
      "transaction_type": "withdrawal",
      "amount": 100.0,
      "description": "ATM withdrawal",
      "status": "completed",
      "created_at": "2026-01-12T15:30:00"
    }
  ],
  "created_at": "2026-01-15T12:00:00"
}
```

**Statement Features:**

- ✅ Customizable date ranges for statement periods
- ✅ Transaction summaries by type (deposits, withdrawals, transfers in/out)
- ✅ Current account balance
- ✅ Complete transaction history for the period
- ✅ Transaction count and categorization
- ✅ JSON output format for easy integration

### Error Tracking & Monitoring 🚨

Admin users can monitor and analyze application errors through the error tracking API.

#### Get Error Summary (Admin Only)

```bash
# First, login as admin user
curl -X POST "http://localhost:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "adminpass"
  }'

# Use the admin token to get error summary
curl "http://localhost:8000/api/v1/admin/errors/summary?hours=24" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

#### List Recent Errors (Admin Only)

```bash
curl "http://localhost:8000/api/v1/admin/errors?category=validation&limit=50" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

**Error Tracking Features:**

- ✅ Automatic error categorization (validation, auth, server, database)
- ✅ PII sanitization in all error logs
- ✅ Error storage in database for analysis
- ✅ Filtering by category, endpoint, status code, date range
- ✅ Detailed stack traces with context
- ✅ Admin-only access with superuser requirement

> **📖 For complete error API documentation and examples, see [ERROR_HANDLING.md](documentation/ERROR_HANDLING.md)**
> **📖 Complete transfer guide with examples:** [TRANSFER_GUIDE.md](documentation/TRANSFER_GUIDE.md)  
> **🔧 Database migration guide:** [TRANSFER_MIGRATION.md](documentation/TRANSFER_MIGRATION.md)  
> **📋 Quick reference:** [TRANSFER_QUICKREF.md](documentation/TRANSFER_QUICKREF.md)

### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" button (🔓 icon at the top)
3. Login at `/api/v1/auth/login` to get your token
4. Enter the token in the authorization dialog
5. All protected endpoints will now work with your credentials

For detailed authentication examples and troubleshooting, see [AUTH_GUIDE.md](documentation/AUTH_GUIDE.md).

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

# Transfer Limits (Optional - defaults provided)
MAX_TRANSFER_AMOUNT=100000.0
DAILY_TRANSFER_LIMIT=500000.0
MIN_TRANSFER_AMOUNT=0.01
MAX_EXTERNAL_TRANSFER_AMOUNT=50000.0
MIN_ACCOUNT_BALANCE=0.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=logs
```

**Security Note:** The `SECRET_KEY` is used to sign JWT tokens. In production:

- Use a strong, randomly generated key (at least 32 characters)
- Never commit real secrets to version control

**Logging Configuration:**

- `LOG_LEVEL`: Set to DEBUG, INFO, WARNING, ERROR, or CRITICAL (default: INFO)
- `LOG_DIR`: Directory where log files will be stored (default: logs)
- See [LOGGING_GUIDE.md](documentation/LOGGING_GUIDE.md) for detailed logging documentation

### Database

The database is automatically created in the `data/` directory when you first run the application.

**For SQLite (Development):**

- ✅ No migrations needed - SQLAlchemy creates all tables automatically
- ✅ To use new features: just delete `data/banking.db` and restart
- ✅ Fresh database created with correct schema every time

**For Production Databases (PostgreSQL/MySQL):**

- ⚠️ Migrations are required when schema changes
- ⚠️ See [TRANSFER_MIGRATION.md](documentation/TRANSFER_MIGRATION.md) for migration scripts
- ⚠️ Consider using Alembic for production migration management

### Models

- **User**: User accounts with authentication credentials (email, username, hashed password)
- **Account**: Bank accounts with account number, holder name, type, and balance
- **Transaction**: Financial transactions (deposits/withdrawals/transfers) linked to accounts
  - Enhanced with transfer fields (destination account, external bank info)
  - Status tracking (pending, completed, failed, reversed)
  - Reference IDs for transfer linking

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

# Transfer tests (NEW)
pytest tests/integration/test_transfers.py -v

# Run transfer tests with detailed output
pytest tests/integration/test_transfers.py -v -s

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

All detailed documentation is located in the [`documentation/`](documentation/) folder:

### Core Documentation
- **[ENVIRONMENT_GUIDE.md](documentation/ENVIRONMENT_GUIDE.md)** - Environment configuration for dev/test/prod
- **[LOGGING_GUIDE.md](documentation/LOGGING_GUIDE.md)** - Structured logging configuration and usage
- **[AUTH_GUIDE.md](documentation/AUTH_GUIDE.md)** - Comprehensive authentication guide with examples
- **[ADMIN_SETUP.md](documentation/ADMIN_SETUP.md)** - Admin user creation and superuser privileges
- **[ERROR_HANDLING.md](documentation/ERROR_HANDLING.md)** - Error tracking, reporting, and PII sanitization
- **[ARCHITECTURE.md](documentation/ARCHITECTURE.md)** - System architecture and design decisions
- **[PROJECT_STRUCTURE.md](documentation/PROJECT_STRUCTURE.md)** - Detailed project structure
- **[MIGRATION_GUIDE.md](documentation/MIGRATION_GUIDE.md)** - Database migration guide

### Transfer System Documentation 💸
- **[TRANSFER_README.md](documentation/TRANSFER_README.md)** - Quick start guide for money transfers
- **[TRANSFER_GUIDE.md](documentation/TRANSFER_GUIDE.md)** - Complete transfer documentation with examples
- **[TRANSFER_MIGRATION.md](documentation/TRANSFER_MIGRATION.md)** - Database migration (for production PostgreSQL/MySQL only)
- **[TRANSFER_IMPLEMENTATION.md](documentation/TRANSFER_IMPLEMENTATION.md)** - Implementation details and summary
- **[TRANSFER_QUICKREF.md](documentation/TRANSFER_QUICKREF.md)** - Quick reference card

### Card System Documentation 💳
- **[CARDS_GUIDE.md](documentation/CARDS_GUIDE.md)** - Complete card management guide with API reference

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

Recently Added:
- [x] Logging and monitoring
- [x] **Secure money transfers with ACID compliance**
- [x] **Internal and external transfer support**
- [x] **Transaction limits and validation**
- [x] **Comprehensive error tracking and reporting system**
- [x] **Admin API for error monitoring with PII sanitization**

Future enhancements planned:
- [ ] Password reset functionality
- [ ] Email verification
- [ ] Refresh token support
- [ ] Role-based access control (RBAC)
- [ ] Account lockout after failed login attempts
- [ ] OAuth2 social login (Google, GitHub)
- [ ] API rate limiting
- [ ] Database migrations with Alembic
- [ ] CI/CD pipeline
- [ ] Scheduled/recurring transfers
- [ ] Real-time transfer notifications
- [ ] Multi-currency support


