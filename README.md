# Banking App API

A starter banking application backend API built with FastAPI and SQLite, featuring Docker support and environment-based configuration.

## Features

- 🚀 FastAPI framework with automatic OpenAPI documentation
- 💾 SQLite database with SQLAlchemy ORM
- 🐳 Docker and Docker Compose support
- 🔒 Environment variable configuration (.env support)
- 📝 Interactive API documentation with Swagger UI
- ✅ Basic banking operations (accounts and transactions)

## Prerequisites

- Python 3.11+ (for local development)
- Docker and Docker Compose (for containerized deployment)

## Project Structure

```
banking_app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration and environment variables
├── database.py          # Database models and setup
├── schemas.py           # Pydantic schemas for validation
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Docker Compose orchestration
├── .env.example         # Environment variables template
└── README.md           # This file
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
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

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
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Root & Health
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Accounts
- `POST /api/v1/accounts` - Create a new bank account
- `GET /api/v1/accounts` - List all accounts
- `GET /api/v1/accounts/{account_id}` - Get account details with transactions
- `DELETE /api/v1/accounts/{account_id}` - Delete an account

### Transactions
- `POST /api/v1/transactions` - Create a new transaction (deposit/withdrawal)
- `GET /api/v1/transactions` - List all transactions
- `GET /api/v1/transactions/{transaction_id}` - Get transaction details

## Example Usage

### Create an Account

```bash
curl -X POST "http://localhost:8000/api/v1/accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "account_holder": "John Doe",
    "account_type": "checking",
    "initial_balance": 1000.0
  }'
```

### Make a Deposit

```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "transaction_type": "deposit",
    "amount": 500.0,
    "description": "Salary deposit"
  }'
```

### Make a Withdrawal

```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "transaction_type": "withdrawal",
    "amount": 200.0,
    "description": "ATM withdrawal"
  }'
```

### Get Account Details

```bash
curl "http://localhost:8000/api/v1/accounts/1"
```

## Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```env
# Database Configuration
DATABASE_URL=sqlite:///./banking.db

# Application Configuration
APP_NAME=Banking App API
APP_VERSION=1.0.0
DEBUG=True

# API Configuration
API_PREFIX=/api/v1

# Security
SECRET_KEY=your-secret-key-here-change-in-production
```

## Database

The application uses SQLite as the database, which is perfect for development and testing. The database file (`banking.db`) is automatically created when you first run the application.

### Models

- **Account**: Represents a bank account with account number, holder name, type, and balance
- **Transaction**: Represents a financial transaction (deposit or withdrawal) linked to an account

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run tests (when implemented)
pytest
```

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
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions, please open an issue on the GitHub repository.
