# Integration Tests

Integration tests verify that different components work together correctly, testing the full API endpoints with a real database.

## Test Coverage

### API Endpoint Tests
- **test_accounts.py**: Tests for account endpoints
  - POST /api/v1/accounts - Create account
  - GET /api/v1/accounts - List accounts
  - GET /api/v1/accounts/{id} - Get specific account
  - DELETE /api/v1/accounts/{id} - Delete account

- **test_transactions.py**: Tests for transaction endpoints
  - POST /api/v1/transactions - Create transaction (deposit/withdrawal)
  - GET /api/v1/transactions - List transactions
  - GET /api/v1/transactions/{id} - Get specific transaction
  - Business logic validation (insufficient balance, etc.)

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_accounts.py -v

# Run with coverage
pytest tests/integration/ --cov=app --cov-report=html
```

## Test Philosophy

- **End-to-End**: Tests complete request-response cycles
- **Real Database**: Uses test database (not mocks)
- **API Contract**: Validates request/response formats
- **Business Scenarios**: Tests real-world use cases
