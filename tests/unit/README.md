# Unit Tests

Unit tests focus on testing individual components in isolation using mocks and stubs.

## Test Coverage

### Repository Tests
- **test_account_repository.py**: Tests for `AccountRepository`
  - Create, read, update, delete operations
  - Query methods
  - Account existence checks

- **test_transaction_repository.py**: Tests for `TransactionRepository`
  - Transaction creation
  - Query methods
  - Filtering by account

### Service Tests
- **test_account_service.py**: Tests for `AccountService`
  - Account number generation
  - Account creation with validation
  - Business logic validation (negative balance, etc.)
  - Error handling

- **test_transaction_service.py**: Tests for `TransactionService`
  - Deposit and withdrawal logic
  - Balance validation
  - Transaction type validation
  - Error handling

## Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_account_service.py -v

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html
```

## Test Philosophy

- **Isolation**: Each test is independent and uses mocks
- **Fast**: No database or external dependencies
- **Focused**: Tests one method/function at a time
- **Comprehensive**: Covers success cases, edge cases, and error scenarios
