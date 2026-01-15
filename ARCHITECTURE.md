# Architecture Documentation

## Repository and Service Layer Pattern

This banking application has been refactored to follow the **Repository and Service Layer Pattern**, which provides better separation of concerns and maintainability.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (main.py)                      │
│                    FastAPI Route Handlers                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer (services.py)                │
│              Business Logic & Validation                     │
│    - AccountService: Account operations & validation        │
│    - TransactionService: Transaction logic & rules          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│               Repository Layer (repositories.py)             │
│                    Data Access Logic                         │
│    - AccountRepository: Account CRUD operations             │
│    - TransactionRepository: Transaction CRUD operations     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer (database.py)               │
│                SQLAlchemy Models & Session                   │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. **API Layer** ([main.py](main.py))
- Handles HTTP requests and responses
- Route definitions and endpoint documentation
- Dependency injection for services
- Response model validation
- **Does NOT contain**: Business logic or direct database access

#### 2. **Service Layer** ([services.py](services.py))
- Contains business logic and rules
- Validation of business constraints
- Orchestrates repository calls
- Error handling and exceptions
- Transaction coordination

**Services:**
- `AccountService`: 
  - Account creation with unique number generation
  - Account validation
  - Account retrieval and deletion
  
- `TransactionService`:
  - Transaction creation with balance validation
  - Withdrawal/deposit logic
  - Transaction history retrieval

#### 3. **Repository Layer** ([repositories.py](repositories.py))
- Data access and persistence
- Database query operations
- CRUD operations
- **Does NOT contain**: Business logic

**Repositories:**
- `AccountRepository`:
  - Create, read, update, delete accounts
  - Query accounts by ID or account number
  - Check account existence
  
- `TransactionRepository`:
  - Create, read transactions
  - Query transactions by account

#### 4. **Database Layer** ([database.py](database.py))
- SQLAlchemy ORM models
- Database connection setup
- Session management

### Benefits of This Architecture

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Testability**: Layers can be tested independently with mock objects
3. **Maintainability**: Changes to business logic don't affect data access code
4. **Reusability**: Services and repositories can be reused across different endpoints
5. **Scalability**: Easy to extend with new features without affecting existing code
6. **Clarity**: Code organization is intuitive and easy to understand

### Usage Example

```python
# In route handlers (main.py)
@app.post("/api/v1/accounts")
def create_account(
    account: AccountCreate, 
    account_service: AccountService = Depends(get_account_service)
):
    # Service handles all business logic
    return account_service.create_account(
        account_holder=account.account_holder,
        account_type=account.account_type,
        initial_balance=account.initial_balance
    )
```

```python
# In services (services.py)
class AccountService:
    def create_account(self, account_holder, account_type, initial_balance):
        # Business logic: generate account number
        account_number = self.generate_account_number()
        
        # Business validation
        if initial_balance < 0:
            raise HTTPException(...)
        
        # Repository handles data access
        return self.repository.create(
            account_number, account_holder, account_type, initial_balance
        )
```

```python
# In repositories (repositories.py)
class AccountRepository:
    def create(self, account_number, account_holder, account_type, balance):
        # Pure data access - no business logic
        db_account = Account(
            account_number=account_number,
            account_holder=account_holder,
            account_type=account_type,
            balance=balance
        )
        self.db.add(db_account)
        self.db.commit()
        return db_account
```

### Testing Strategy

With this architecture, you can easily test each layer:

```python
# Test service layer with mocked repository
def test_create_account():
    mock_repo = Mock(AccountRepository)
    service = AccountService(db=mock_db)
    service.repository = mock_repo
    # Test business logic...

# Test repository layer with test database
def test_account_repository():
    repo = AccountRepository(test_db)
    account = repo.create("1234567890", "John Doe", "checking", 100.0)
    assert account.balance == 100.0
```

### Future Enhancements

This architecture makes it easy to add:
- Unit of Work pattern for complex transactions
- Caching layer in services
- Event-driven architecture with domain events
- Additional repositories and services
- Background tasks and async operations
