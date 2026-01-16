# Money Transfer System Documentation

## Overview

This banking application implements a secure money transfer system with ACID compliance, transaction limits, and comprehensive validation. The system supports both internal transfers (between accounts within the system) and external transfers (to accounts at other banks).

## Features

### 🔒 Security & Compliance

- **ACID Compliance**: All transfers use database transactions with automatic rollback on failure
- **Balance Validation**: Ensures sufficient funds before initiating transfers
- **Transaction Limits**: Enforces single transaction and daily transfer limits
- **Audit Trail**: Complete logging of all transfer attempts and outcomes
- **Authentication Required**: All transfer operations require valid JWT authentication

### 💸 Transfer Types

#### Internal Transfers

- Transfer money between accounts within the same banking system
- Instant completion with atomic debit/credit operations
- Both source and destination transactions logged
- Linked via unique reference ID

#### External Transfers

- Transfer money to accounts at external banks
- Validates external account details (account number, routing number)
- Starts in "pending" status awaiting external processing
- Lower transaction limits for security

## Transfer Flow

### 1. Transfer Request Validation

```
POST /api/v1/transfers/internal or /api/v1/transfers/external
↓
Authentication Check (JWT Token)
↓
Schema Validation (amount, account numbers, etc.)
```

### 2. Account Validation

```
Validate Source Account Exists
↓
Validate Destination Account (internal) or External Details
↓
Ensure Accounts Are Different (internal only)
```

### 3. Balance & Limits Check

```
Check Source Account Balance
↓
Verify Minimum Balance Requirements
↓
Check Single Transfer Limit
↓
Check Daily Transfer Limit
```

### 4. Transaction Execution (ACID)

```
BEGIN DATABASE TRANSACTION
↓
Debit Source Account
↓
Create Debit Transaction Record
↓
Credit Destination (internal) / Mark Pending (external)
↓
Create Credit Transaction Record (internal only)
↓
COMMIT (Success) or ROLLBACK (Failure)
```

### 5. Confirmation & Logging

```
Generate Transfer Reference ID
↓
Log Transaction Details
↓
Return Transfer Confirmation
```

### 6. Error Handling

```
If Any Step Fails:
↓
ROLLBACK All Changes
↓
Log Error Details
↓
Return User-Friendly Error Message
```

## API Endpoints

### Create Internal Transfer

**POST** `/api/v1/transfers/internal`

**Request Body:**

```json
{
  "source_account_id": 1,
  "destination_account_id": 2,
  "amount": 100.00,
  "description": "Payment for services"
}
```

**Response:** (201 Created)

```json
{
  "transfer_id": "TXN-A1B2C3D4E5F6",
  "source_transaction_id": 123,
  "destination_transaction_id": 124,
  "transfer_type": "internal",
  "amount": 100.00,
  "status": "completed",
  "source_account_id": 1,
  "destination_account_id": 2,
  "description": "Payment for services",
  "created_at": "2026-01-15T10:30:00Z"
}
```

### Create External Transfer

**POST** `/api/v1/transfers/external`

**Request Body:**

```json
{
  "source_account_id": 1,
  "external_account_number": "1234567890",
  "external_bank_name": "External Bank Corp",
  "external_routing_number": "123456789",
  "amount": 500.00,
  "description": "Payment to external account"
}
```

**Response:** (201 Created)

```json
{
  "transfer_id": "EXT-X9Y8Z7W6V5U4",
  "source_transaction_id": 125,
  "destination_transaction_id": null,
  "transfer_type": "external",
  "amount": 500.00,
  "status": "pending",
  "source_account_id": 1,
  "destination_account_id": null,
  "external_account_number": "1234567890",
  "external_bank_name": "External Bank Corp",
  "description": "Payment to external account",
  "created_at": "2026-01-15T10:35:00Z"
}
```

### Get Transfer Details

**GET** `/api/v1/transfers/{reference_id}`

**Response:** (200 OK)

```json
{
  "transfer_id": "TXN-A1B2C3D4E5F6",
  "source_transaction_id": 123,
  "destination_transaction_id": 124,
  "transfer_type": "internal",
  "amount": 100.00,
  "status": "completed",
  "source_account_id": 1,
  "destination_account_id": 2,
  "description": "Payment for services",
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

## Configuration

Transfer limits are configured in `app/core/config.py`:

```python
# Transfer Limits Configuration
max_transfer_amount: float = 100000.0      # Max single transfer
daily_transfer_limit: float = 500000.0     # Max daily total
min_transfer_amount: float = 0.01          # Minimum transfer
max_external_transfer_amount: float = 50000.0  # Max external transfer
min_account_balance: float = 0.0           # Minimum balance after transfer
```

These can be overridden via environment variables:

```bash
MAX_TRANSFER_AMOUNT=200000.0
DAILY_TRANSFER_LIMIT=1000000.0
MIN_TRANSFER_AMOUNT=1.0
MAX_EXTERNAL_TRANSFER_AMOUNT=100000.0
MIN_ACCOUNT_BALANCE=100.0
```

## Validation Rules

### Internal Transfers

- ✅ Source and destination accounts must exist
- ✅ Source and destination must be different accounts
- ✅ Amount must be >= `min_transfer_amount`
- ✅ Amount must be <= `max_transfer_amount`
- ✅ Source balance must be >= amount
- ✅ Remaining balance must be >= `min_account_balance`
- ✅ Daily total must not exceed `daily_transfer_limit`

### External Transfers

- ✅ Source account must exist
- ✅ External account number must be 8-20 digits
- ✅ External routing number must be exactly 9 digits
- ✅ Amount must be >= `min_transfer_amount`
- ✅ Amount must be <= `max_external_transfer_amount` (lower than internal)
- ✅ Source balance must be >= amount
- ✅ Remaining balance must be >= `min_account_balance`
- ✅ Daily total must not exceed `daily_transfer_limit`

## Error Handling

### Common Error Responses

**400 Bad Request** - Validation Error

```json
{
  "detail": "Insufficient balance. Available: $500.00, Required: $1000.00"
}
```

**400 Bad Request** - Limit Exceeded

```json
{
  "detail": "Transfer amount exceeds maximum limit ($100,000.00)"
}
```

**400 Bad Request** - Daily Limit

```json
{
  "detail": "Transfer would exceed daily limit. Used: $450,000.00, Limit: $500,000.00"
}
```

**404 Not Found** - Account Not Found

```json
{
  "detail": "Source account not found"
}
```

**401 Unauthorized** - Authentication Required

```json
{
  "detail": "Could not validate credentials"
}
```

**500 Internal Server Error** - System Error

```json
{
  "detail": "Transfer failed due to database error. Transaction has been rolled back."
}
```

## Database Schema

### Enhanced Transaction Model

```python
class Transaction(Base):
    __tablename__ = "transactions"
    
    id: int                              # Primary key
    account_id: int                      # Foreign key to accounts
    transaction_type: str                # deposit, withdrawal, transfer_out, transfer_in
    amount: float                        # Transaction amount
    description: str                     # Optional description
    
    # Transfer-specific fields
    transfer_type: str                   # internal, external (nullable)
    destination_account_id: int          # For internal transfers (nullable)
    external_account_number: str         # For external transfers (nullable)
    external_bank_name: str              # For external transfers (nullable)
    external_routing_number: str         # For external transfers (nullable)
    
    # Status tracking
    status: str                          # pending, completed, failed, reversed
    reference_id: str                    # Unique transfer reference (indexed)
    
    created_at: datetime                 # Creation timestamp
    updated_at: datetime                 # Last update timestamp
```

## Transaction States

| Status | Description | Used For |
|--------|-------------|----------|
| `pending` | Transfer initiated but not completed | External transfers |
| `completed` | Transfer successfully processed | All successful transfers |
| `failed` | Transfer attempt failed | Failed transfers (rare) |
| `reversed` | Transfer was reversed/refunded | Reversals |

## ACID Compliance Implementation

### Atomicity

All transfer operations are wrapped in database transactions. Either all changes succeed, or all are rolled back.

```python
try:
    # Debit source account
    source_account.balance -= amount
    
    # Create debit transaction
    db.add(source_transaction)
    
    # Credit destination account (internal only)
    dest_account.balance += amount
    
    # Create credit transaction (internal only)
    db.add(dest_transaction)
    
    # Commit all changes together
    db.commit()
except Exception:
    # Rollback all changes
    db.rollback()
    raise
```

### Consistency

- Balance validations ensure accounts never go negative
- Transaction records always match account balance changes
- Reference IDs link related transactions

### Isolation

Database transactions provide isolation between concurrent transfers.

### Durability

Once committed, transfers are permanently recorded in the database.

## Security Considerations

### Authentication & Authorization

- All endpoints require JWT authentication
- Users can only access their own account transfers (implement authorization)

### Data Validation

- Input validation using Pydantic schemas
- Type checking and range validation
- Format validation for account numbers

### Audit Logging

- All transfer attempts logged with structured logging
- Includes user ID, account IDs, amounts, and outcomes
- Failed attempts logged for security monitoring

### Rate Limiting (Recommended)

Consider implementing rate limiting to prevent:

- Brute force attacks
- API abuse
- Denial of service

## Testing

Run the transfer tests:

```bash
# Run all transfer tests
pytest tests/integration/test_transfers.py -v

# Run specific test class
pytest tests/integration/test_transfers.py::TestInternalTransfers -v

# Run with coverage
pytest tests/integration/test_transfers.py --cov=app.services.transfer_service
```

## Future Enhancements

### Phase 2 Features

- [ ] Scheduled/recurring transfers
- [ ] Multi-currency support
- [ ] Transfer templates
- [ ] Batch transfers
- [ ] Transfer cancellation (pending only)

### Phase 3 Features

- [ ] Real-time notifications (email, SMS)
- [ ] Webhook support for external systems
- [ ] Advanced fraud detection
- [ ] Transfer reversal workflow
- [ ] Mobile push notifications

## Monitoring & Observability

### Key Metrics to Monitor

- Transfer success rate
- Average transfer amount
- Daily transfer volume
- Failed transfer reasons
- Transfer latency (p50, p95, p99)

### Logs to Watch

- Insufficient balance attempts
- Limit exceeded attempts
- Failed database transactions
- Unusual transfer patterns

### Alerts to Configure

- High failure rate (> 5%)
- Unusual transfer volume
- Database transaction errors
- External API failures (when implemented)

## Support & Troubleshooting

### Common Issues

**Issue**: Transfer fails with "insufficient balance"

- **Cause**: Account balance is less than transfer amount
- **Solution**: Verify account balance before initiating transfer

**Issue**: Transfer rejected due to limits

- **Cause**: Amount exceeds configured limits
- **Solution**: Check transfer limits in configuration

**Issue**: "Account not found" error

- **Cause**: Account ID doesn't exist or was deleted
- **Solution**: Verify account exists and is active

**Issue**: External transfer stuck in "pending"

- **Cause**: External processing not yet implemented
- **Solution**: Implement webhook handler for status updates

## API Examples

### Using curl

```bash
# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password" | jq -r .access_token)

# Create internal transfer
curl -X POST http://localhost:8000/api/v1/transfers/internal \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_account_id": 1,
    "destination_account_id": 2,
    "amount": 100.00,
    "description": "Test transfer"
  }'

# Get transfer details
curl -X GET http://localhost:8000/api/v1/transfers/TXN-A1B2C3D4E5F6 \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "testuser", "password": "password"}
)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Create internal transfer
transfer_data = {
    "source_account_id": 1,
    "destination_account_id": 2,
    "amount": 100.00,
    "description": "Test transfer"
}

response = requests.post(
    "http://localhost:8000/api/v1/transfers/internal",
    json=transfer_data,
    headers=headers
)

transfer = response.json()
print(f"Transfer ID: {transfer['transfer_id']}")
print(f"Status: {transfer['status']}")
```

## Conclusion

This transfer system provides a robust, secure, and scalable foundation for money transfers in a banking application. The ACID-compliant implementation ensures data integrity, while comprehensive validation and error handling provide a reliable user experience.
