# Production-Ready FastAPI Project Structure

This document describes the new production-ready directory structure of the Banking App API.

## Directory Structure

```
banking_app_backend/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   └── v1/                    # API version 1
│   │       ├── __init__.py
│   │       └── endpoints/         # API endpoints/routes
│   │           ├── accounts.py    # Account endpoints
│   │           └── transactions.py # Transaction endpoints
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py             # Application configuration
│   │   ├── database.py           # Database setup and session
│   │   └── dependencies.py       # FastAPI dependencies
│   │
│   ├── models/                    # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── account.py            # Account model
│   │   └── transaction.py        # Transaction model
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── account_repository.py # Account data access
│   │   └── transaction_repository.py # Transaction data access
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── account.py            # Account schemas
│   │   └── transaction.py        # Transaction schemas
│   │
│   └── services/                  # Business logic layer
│       ├── __init__.py
│       ├── account_service.py    # Account business logic
│       └── transaction_service.py # Transaction business logic
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── test_accounts.py          # Account endpoint tests
│   └── test_transactions.py      # Transaction endpoint tests
│
├── main.py                        # FastAPI application entry point
├── .env                          # Environment variables
├── .env.example                  # Example environment file
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
└── README.md                     # Project documentation
```

## Layer Descriptions

### 1. **API Layer** (`app/api/`)
- **Purpose**: Define HTTP endpoints and route handlers
- **Structure**: Organized by API version (v1, v2, etc.)
- **Responsibilities**:
  - Route definitions
  - Request/response handling
  - HTTP status codes
  - Endpoint documentation

**Example**: [app/api/v1/endpoints/accounts.py](app/api/v1/endpoints/accounts.py)
```python
router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("", response_model=AccountResponse)
def create_account(account: AccountCreate, service: AccountService = Depends(...)):
    return service.create_account(...)
```

### 2. **Core Layer** (`app/core/`)
- **Purpose**: Core application setup and shared utilities
- **Components**:
  - `config.py`: Application settings and configuration
  - `database.py`: Database connection and session management
  - `dependencies.py`: FastAPI dependency injection functions

**Example**: [app/core/dependencies.py](app/core/dependencies.py)
```python
def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    return AccountService(db)
```

### 3. **Models Layer** (`app/models/`)
- **Purpose**: Define database table structures
- **Technology**: SQLAlchemy ORM models
- **Responsibilities**:
  - Table definitions
  - Column specifications
  - Relationships between tables

**Example**: [app/models/account.py](app/models/account.py)
```python
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    account_number = Column(String, unique=True)
    balance = Column(Float, default=0.0)
```

### 4. **Repositories Layer** (`app/repositories/`)
- **Purpose**: Handle all database operations
- **Pattern**: Repository pattern
- **Responsibilities**:
  - CRUD operations
  - Database queries
  - Data persistence

**Example**: [app/repositories/account_repository.py](app/repositories/account_repository.py)
```python
class AccountRepository:
    def create(self, account_number, account_holder, account_type, balance):
        # Database insert logic
        
    def get_by_id(self, account_id):
        # Database query logic
```

### 5. **Schemas Layer** (`app/schemas/`)
- **Purpose**: Define data validation and serialization
- **Technology**: Pydantic models
- **Responsibilities**:
  - Request validation
  - Response serialization
  - Data type enforcement

**Example**: [app/schemas/account.py](app/schemas/account.py)
```python
class AccountCreate(BaseModel):
    account_holder: str
    account_type: str
    initial_balance: float = 0.0
```

### 6. **Services Layer** (`app/services/`)
- **Purpose**: Implement business logic
- **Pattern**: Service pattern
- **Responsibilities**:
  - Business rules and validation
  - Transaction coordination
  - Error handling
  - Orchestration of repository calls

**Example**: [app/services/account_service.py](app/services/account_service.py)
```python
class AccountService:
    def create_account(self, account_holder, account_type, initial_balance):
        # Business validation
        account_number = self.generate_account_number()
        # Repository call
        return self.repository.create(...)
```

### 7. **Tests Layer** (`tests/`)
- **Purpose**: Automated testing
- **Framework**: Pytest
- **Types**:
  - Unit tests
  - Integration tests
  - API endpoint tests

**Example**: [tests/test_accounts.py](tests/test_accounts.py)
```python
def test_create_account(client):
    response = client.post("/api/v1/accounts", json={...})
    assert response.status_code == 201
```

## Architecture Flow

```
HTTP Request
    ↓
API Endpoint (app/api/v1/endpoints/)
    ↓
Service Layer (app/services/)
    ↓
Repository Layer (app/repositories/)
    ↓
Database (via SQLAlchemy Models in app/models/)
```

## Benefits of This Structure

### 1. **Scalability**
- Easy to add new API versions (v2, v3)
- New features can be added without affecting existing code
- Clear separation allows multiple teams to work simultaneously

### 2. **Maintainability**
- Each layer has a single responsibility
- Changes to business logic don't affect data access
- Easy to locate and fix bugs

### 3. **Testability**
- Each layer can be tested independently
- Mock objects can replace dependencies
- Clear testing strategy for each component

### 4. **Reusability**
- Services can be reused across different endpoints
- Repositories can be shared between services
- Consistent patterns across the application

### 5. **Professional Standards**
- Follows FastAPI best practices
- Industry-standard architecture
- Easy for new developers to understand

## Running the Application

### Development
```bash
# Activate virtual environment
source banking_env/bin/activate

# Run with auto-reload
uvicorn main:app --reload
```

### Production
```bash
# Using Docker
docker-compose up --build
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

Configure in `.env` file:
```env
DATABASE_URL=sqlite:////tmp/banking.db
APP_NAME=Banking App API
APP_VERSION=1.0.0
DEBUG=True
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-here
```

## Migration from Old Structure

### Old Structure
```
banking_app_backend/
├── main.py (all routes)
├── config.py
├── database.py (models + db setup)
├── schemas.py
├── services.py
└── repositories.py
```

### New Structure Benefits
- ✅ Organized by feature/layer
- ✅ Easier to navigate
- ✅ Better version control
- ✅ Production-ready
- ✅ Follows FastAPI best practices

## Adding New Features

### Example: Adding a new "Transfers" feature

1. **Create model**: `app/models/transfer.py`
2. **Create schema**: `app/schemas/transfer.py`
3. **Create repository**: `app/repositories/transfer_repository.py`
4. **Create service**: `app/services/transfer_service.py`
5. **Create endpoint**: `app/api/v1/endpoints/transfers.py`
6. **Add router**: Update `app/api/v1/__init__.py`
7. **Add tests**: `tests/test_transfers.py`

This structure makes it clear where each piece belongs!
