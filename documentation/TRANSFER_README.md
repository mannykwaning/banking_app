# 💸 Secure Money Transfer System

## Quick Start

### 1. Create Internal Transfer

```bash
POST /api/v1/transfers/internal
```

```json
{
  "source_account_id": 1,
  "destination_account_id": 2,
  "amount": 100.00,
  "description": "Payment for lunch"
}
```

### 2. Create External Transfer

```bash
POST /api/v1/transfers/external
```

```json
{
  "source_account_id": 1,
  "external_account_number": "9876543210",
  "external_bank_name": "Other Bank",
  "external_routing_number": "123456789",
  "amount": 500.00,
  "description": "Payment to vendor"
}
```

### 3. Check Transfer Status

```bash
GET /api/v1/transfers/{transfer_id}
```

## Features

### ✅ ACID Compliance

- **Atomic**: All operations succeed or fail together
- **Consistent**: Balances always match transaction records
- **Isolated**: Concurrent transfers don't interfere
- **Durable**: Committed transfers are permanent

### ✅ Security

- JWT authentication required
- Input validation and sanitization
- Comprehensive audit logging
- Balance and limit checks

### ✅ Validation

- Sufficient balance verification
- Transaction amount limits
- Daily transfer limits
- Account existence checks
- External account format validation

### ✅ Error Handling

- Automatic rollback on failure
- User-friendly error messages
- Detailed error logging
- Complete audit trail

## Transfer Limits

| Limit Type | Default Value | Description |
|------------|---------------|-------------|
| Min Transfer | $0.01 | Minimum amount per transfer |
| Max Internal Transfer | $100,000 | Maximum internal transfer |
| Max External Transfer | $50,000 | Maximum external transfer |
| Daily Limit | $500,000 | Total daily transfer limit |
| Min Balance | $0.00 | Minimum account balance |

## Transfer States

```
Internal Transfer Flow:
Request → Validate → Check Balance → Check Limits → Execute → Completed

External Transfer Flow:
Request → Validate → Check Balance → Check Limits → Execute → Pending → Processing
```

## API Reference

### Internal Transfer

**Endpoint:** `POST /api/v1/transfers/internal`

**Authentication:** Bearer Token Required

**Request Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source_account_id | integer | Yes | Source account ID |
| destination_account_id | integer | Yes | Destination account ID |
| amount | number | Yes | Transfer amount (> 0) |
| description | string | No | Transfer description |

**Response Schema:**

```typescript
{
  transfer_id: string,              // Unique reference (TXN-XXX)
  source_transaction_id: number,
  destination_transaction_id: number,
  transfer_type: "internal",
  amount: number,
  status: "completed",
  source_account_id: number,
  destination_account_id: number,
  description: string | null,
  created_at: datetime
}
```

### External Transfer

**Endpoint:** `POST /api/v1/transfers/external`

**Authentication:** Bearer Token Required

**Request Schema:**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| source_account_id | integer | Yes | Must exist |
| external_account_number | string | Yes | 8-20 digits |
| external_bank_name | string | Yes | 2-100 chars |
| external_routing_number | string | Yes | Exactly 9 digits |
| amount | number | Yes | > 0 |
| description | string | No | Optional |

**Response Schema:**

```typescript
{
  transfer_id: string,              // Unique reference (EXT-XXX)
  source_transaction_id: number,
  destination_transaction_id: null,
  transfer_type: "external",
  amount: number,
  status: "pending",
  source_account_id: number,
  external_account_number: string,
  external_bank_name: string,
  description: string | null,
  created_at: datetime
}
```

### Get Transfer

**Endpoint:** `GET /api/v1/transfers/{reference_id}`

**Authentication:** Bearer Token Required

**Path Parameters:**

- `reference_id`: Transfer reference ID (TXN-XXX or EXT-XXX)

**Response:** Same as transfer creation response with updated status

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Insufficient balance. Available: $500.00, Required: $1000.00"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Source account not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Transfer failed. Transaction has been rolled back."
}
```

## Code Examples

### Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]

# Create transfer
headers = {"Authorization": f"Bearer {token}"}
transfer = {
    "source_account_id": 1,
    "destination_account_id": 2,
    "amount": 100.00,
    "description": "Payment"
}

response = requests.post(
    "http://localhost:8000/api/v1/transfers/internal",
    json=transfer,
    headers=headers
)

result = response.json()
print(f"Transfer ID: {result['transfer_id']}")
print(f"Status: {result['status']}")
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=user&password=pass'
});
const { access_token } = await loginResponse.json();

// Create transfer
const transfer = {
  source_account_id: 1,
  destination_account_id: 2,
  amount: 100.00,
  description: 'Payment'
};

const response = await fetch('http://localhost:8000/api/v1/transfers/internal', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(transfer)
});

const result = await response.json();
console.log(`Transfer ID: ${result.transfer_id}`);
console.log(`Status: ${result.status}`);
```

### cURL

```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=pass" | jq -r .access_token)

# Create internal transfer
curl -X POST http://localhost:8000/api/v1/transfers/internal \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_account_id": 1,
    "destination_account_id": 2,
    "amount": 100.00,
    "description": "Payment"
  }'

# Get transfer status
curl -X GET http://localhost:8000/api/v1/transfers/TXN-A1B2C3D4E5F6 \
  -H "Authorization: Bearer $TOKEN"
```

## Testing

### Run Tests

```bash
# All transfer tests
pytest tests/integration/test_transfers.py -v

# Specific test class
pytest tests/integration/test_transfers.py::TestInternalTransfers -v

# With coverage
pytest tests/integration/test_transfers.py --cov=app.services.transfer_service --cov-report=html
```

### Test Coverage

- ✅ Successful transfers (internal & external)
- ✅ Insufficient balance
- ✅ Same account transfer rejection
- ✅ Transfer limit enforcement
- ✅ Daily limit enforcement
- ✅ Account validation
- ✅ ACID compliance (rollback on failure)
- ✅ API endpoint integration

## Configuration

### Environment Variables

```bash
# .env file
MAX_TRANSFER_AMOUNT=100000.0
DAILY_TRANSFER_LIMIT=500000.0
MIN_TRANSFER_AMOUNT=0.01
MAX_EXTERNAL_TRANSFER_AMOUNT=50000.0
MIN_ACCOUNT_BALANCE=0.0
```

### Code Configuration

```python
# app/core/config.py
class Settings(BaseSettings):
    max_transfer_amount: float = 100000.0
    daily_transfer_limit: float = 500000.0
    min_transfer_amount: float = 0.01
    max_external_transfer_amount: float = 50000.0
    min_account_balance: float = 0.0
```

## Database Schema

### Transaction Fields

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL,
    transaction_type VARCHAR NOT NULL,  -- deposit, withdrawal, transfer_out, transfer_in
    amount FLOAT NOT NULL,
    description VARCHAR,
    
    -- Transfer fields
    transfer_type VARCHAR,              -- internal, external
    destination_account_id INTEGER,
    external_account_number VARCHAR,
    external_bank_name VARCHAR,
    external_routing_number VARCHAR,
    
    -- Status
    status VARCHAR DEFAULT 'completed', -- pending, completed, failed, reversed
    reference_id VARCHAR,               -- Unique transfer reference
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (destination_account_id) REFERENCES accounts(id)
);

CREATE INDEX idx_transactions_reference_id ON transactions(reference_id);
```

## Architecture

### Service Layer

```
TransferService
├── _validate_accounts()      # Validate source/destination
├── _check_balance()           # Verify sufficient funds
├── _check_transfer_limits()   # Enforce limits
├── _execute_internal_transfer() # ACID internal transfer
├── _execute_external_transfer() # ACID external transfer
├── create_internal_transfer()   # Public API
├── create_external_transfer()   # Public API
└── get_transfer_by_reference_id() # Query transfers
```

### Flow Diagram

```
┌─────────────────┐
│  API Request    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Authenticate   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validate Input │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate        │
│ Accounts        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Balance   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Limits    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BEGIN           │
│ TRANSACTION     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Debit Source    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Credit Dest     │
│ (if internal)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Txn      │
│ Records         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ COMMIT          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Log & Return    │
└─────────────────┘
```

## Monitoring

### Metrics to Track

- Transfer success rate
- Average transfer amount
- Daily transfer volume
- Failed transfer count
- Transfer latency (p50, p95, p99)

### Log Levels

```python
INFO  - Successful transfers
WARN  - Validation failures (insufficient balance, limits)
ERROR - System failures (database errors, unexpected exceptions)
```

### Sample Logs

```
INFO - Internal transfer requested: reference_id=TXN-ABC123, source=1, dest=2, amount=100.0
INFO - Internal transfer completed: reference_id=TXN-ABC123, source_txn=123, dest_txn=124
WARN - Transfer failed - insufficient balance: account=1, balance=50.0, amount=100.0
ERROR - Internal transfer failed - database error: reference_id=TXN-ABC123, error=...
```

## Troubleshooting

### Common Issues

**Q: Transfer fails with "insufficient balance" but account has money**
A: Check if the transfer would bring balance below `min_account_balance`

**Q: Getting "exceeds maximum limit" error**
A: Check both single transfer limit and daily limit. Use smaller amounts or wait for daily reset.

**Q: External transfer stuck in "pending"**
A: External transfers require additional processing. Implement webhook handlers for status updates.

**Q: "Account not found" error**
A: Verify account exists and ID is correct. Check for soft-deleted accounts.

## Documentation

- 📖 [Complete Transfer Guide](./TRANSFER_GUIDE.md)
- 🔄 [Database Migration Guide](./TRANSFER_MIGRATION.md)
- 🏗️ [Architecture Documentation](./ARCHITECTURE.md)
- 🔐 [Security Best Practices](./AUTH_GUIDE.md)

## Support

For issues or questions:

1. Check logs in `logs/` directory
2. Review error messages and HTTP status codes
3. Verify configuration settings
4. Run integration tests
5. Check database schema matches models

## License

[Your License Here]
