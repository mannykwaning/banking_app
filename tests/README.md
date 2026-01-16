# Testing Guide

Comprehensive testing suite for the Banking App API with separate unit and integration tests.

## Test Structure

```
tests/
├── __init__.py
├── unit/                              # Unit tests (36 tests)
│   ├── conftest.py                   # Unit test fixtures
│   ├── test_account_repository.py    # AccountRepository tests
│   ├── test_account_service.py       # AccountService tests
│   ├── test_transaction_repository.py # TransactionRepository tests
│   ├── test_transaction_service.py   # TransactionService tests
│   └── README.md
└── integration/                       # Integration tests (10 tests)
    ├── conftest.py                   # Integration test fixtures
    ├── test_accounts.py              # Account API endpoint tests
    ├── test_transactions.py          # Transaction API endpoint tests
    └── README.md
```

## Test Coverage

### Unit Tests (36 tests)

Tests individual components in isolation using mocks:

- **Repository Layer** (13 tests)
  - Account CRUD operations
  - Transaction CRUD operations
  - Query and filter methods

- **Service Layer** (23 tests)
  - Business logic validation
  - Error handling
  - Account number generation
  - Balance calculations
  - Transaction processing

### Integration Tests (10 tests)

Tests complete API endpoints with real database:

- **Account Endpoints** (5 tests)
  - Create, list, get, delete accounts
  - Error scenarios

- **Transaction Endpoints** (5 tests)
  - Deposits and withdrawals
  - Balance validation
  - Transaction history

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Unit Tests Only

```bash
pytest tests/unit/ -v
```

### Run Integration Tests Only

```bash
pytest tests/integration/ -v
```

### Run Specific Test File

```bash
pytest tests/unit/test_account_service.py -v
```

### Run Specific Test

```bash
pytest tests/unit/test_account_service.py::TestAccountService::test_create_account_success -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### Run with Coverage Terminal Report

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## Test Results

### Total: 46 tests

- ✅ Unit Tests: 36 passed
- ✅ Integration Tests: 10 passed

## Writing New Tests

### Unit Test Example

```python
from unittest.mock import Mock
import pytest

class TestMyService:
    def test_my_method(self, mock_db_session):
        # Arrange
        service = MyService(mock_db_session)
        service.repository.some_method = Mock(return_value="result")
        
        # Act
        result = service.my_method()
        
        # Assert
        assert result == "result"
        service.repository.some_method.assert_called_once()
```

### Integration Test Example

```python
def test_my_endpoint(client):
    # Act
    response = client.post("/api/v1/resource", json={...})
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["field"] == "expected_value"
```

## Best Practices

### Unit Tests

- ✅ Use mocks for dependencies
- ✅ Test one method at a time
- ✅ Cover success cases and error scenarios
- ✅ Fast execution (no real database)
- ✅ Independent and isolated

### Integration Tests

- ✅ Test complete user workflows
- ✅ Use real database (test DB)
- ✅ Validate API contracts
- ✅ Test error responses
- ✅ Clean up after each test

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ -v --cov=app --cov-report=xml
```

## Dependencies

Test dependencies are listed in `requirements.txt`:

- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin
- `httpx` - HTTP client for TestClient

## Troubleshooting

### Import Errors

Make sure you're running from the project root:

```bash
cd /path/to/banking_app_backend
pytest tests/
```

### Database Issues

Integration tests create a test database that's cleaned up after each test.
Check `tests/integration/conftest.py` for configuration.

### Mock Issues

Ensure mocks are properly configured in `tests/unit/conftest.py`.

## Test Philosophy

**Unit Tests**: Focus on testing individual components in isolation

- Fast feedback
- Easy to debug
- No external dependencies

**Integration Tests**: Focus on testing the system as a whole

- Real-world scenarios
- API contract validation
- End-to-end workflows

Both test types complement each other to provide comprehensive coverage!
