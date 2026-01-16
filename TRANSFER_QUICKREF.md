# Transfer System Quick Reference

## API Endpoints

### Create Internal Transfer

```http
POST /api/v1/transfers/internal
Authorization: Bearer {token}
Content-Type: application/json

{
  "source_account_id": 1,
  "destination_account_id": 2,
  "amount": 100.00,
  "description": "Payment"
}
```

### Create External Transfer

```http
POST /api/v1/transfers/external
Authorization: Bearer {token}
Content-Type: application/json

{
  "source_account_id": 1,
  "external_account_number": "1234567890",
  "external_bank_name": "Other Bank",
  "external_routing_number": "123456789",
  "amount": 500.00,
  "description": "Payment"
}
```

### Get Transfer Status

```http
GET /api/v1/transfers/{reference_id}
Authorization: Bearer {token}
```

## Transfer Limits

| Limit | Default | Env Variable |
|-------|---------|--------------|
| Min Transfer | $0.01 | MIN_TRANSFER_AMOUNT |
| Max Internal | $100,000 | MAX_TRANSFER_AMOUNT |
| Max External | $50,000 | MAX_EXTERNAL_TRANSFER_AMOUNT |
| Daily Limit | $500,000 | DAILY_TRANSFER_LIMIT |
| Min Balance | $0.00 | MIN_ACCOUNT_BALANCE |

## Response Codes

| Code | Meaning |
|------|---------|
| 201 | Transfer created successfully |
| 400 | Validation error (balance, limits, etc.) |
| 401 | Authentication required |
| 404 | Account/transfer not found |
| 500 | Server error (transaction rolled back) |

## Transfer States

- **completed**: Internal transfers (instant)
- **pending**: External transfers (awaiting processing)
- **failed**: Transfer attempt failed
- **reversed**: Transfer was reversed

## Common Errors

### Insufficient Balance

```json
{
  "detail": "Insufficient balance. Available: $X, Required: $Y"
}
```

### Limit Exceeded

```json
{
  "detail": "Transfer amount exceeds maximum limit ($X)"
}
```

### Daily Limit

```json
{
  "detail": "Transfer would exceed daily limit. Used: $X, Limit: $Y"
}
```

## Validation Rules

### Internal Transfer

- ✅ Both accounts must exist
- ✅ Accounts must be different
- ✅ Amount: min_transfer_amount ≤ amount ≤ max_transfer_amount
- ✅ Balance: source_balance ≥ amount
- ✅ Daily: daily_total + amount ≤ daily_limit

### External Transfer

- ✅ Source account must exist
- ✅ Account number: 8-20 digits
- ✅ Routing number: exactly 9 digits
- ✅ Amount: min_transfer_amount ≤ amount ≤ max_external_transfer_amount
- ✅ Balance: source_balance ≥ amount
- ✅ Daily: daily_total + amount ≤ daily_limit

## Files Modified/Created

```
app/
├── models/transaction.py          (Enhanced)
├── schemas/transaction.py         (Enhanced)
├── services/
│   ├── transfer_service.py        (NEW)
│   └── __init__.py               (Updated)
├── api/v1/
│   ├── endpoints/transfers.py     (NEW)
│   └── __init__.py               (Updated)
└── core/
    ├── config.py                  (Updated)
    └── dependencies.py            (Updated)

tests/integration/
├── test_transfers.py              (NEW)
└── conftest.py                    (Updated)

Documentation:
├── TRANSFER_README.md             (NEW)
├── TRANSFER_GUIDE.md              (NEW)
├── TRANSFER_MIGRATION.md          (NEW)
└── TRANSFER_IMPLEMENTATION.md     (NEW)
```

## Testing

```bash
# Run all transfer tests
pytest tests/integration/test_transfers.py -v

# Run with coverage
pytest tests/integration/test_transfers.py --cov=app.services.transfer_service

# Run specific test
pytest tests/integration/test_transfers.py::TestInternalTransfers::test_successful_internal_transfer -v
```

## Database Migration

### SQLite

```bash
sqlite3 banking_app.db < migration.sql
```

### PostgreSQL

```bash
psql -U postgres -d banking_db -f migration.sql
```

See [TRANSFER_MIGRATION.md](TRANSFER_MIGRATION.md) for full details.

## Monitoring

### Key Metrics

- Transfer success rate
- Average transfer amount
- Daily transfer volume
- Failed transfer count

### Log Patterns

```
INFO - Transfer completed: reference_id=TXN-XXX
WARN - Insufficient balance: account_id=X
ERROR - Transfer failed: reference_id=TXN-XXX
```

## Security

- 🔒 JWT authentication required
- 🔒 Input validation (Pydantic schemas)
- 🔒 SQL injection prevention (ORM)
- 🔒 ACID compliance (automatic rollback)
- 🔒 Comprehensive audit logging

## Support

**Documentation:**

- Quick Start: [TRANSFER_README.md](TRANSFER_README.md)
- Complete Guide: [TRANSFER_GUIDE.md](TRANSFER_GUIDE.md)
- Migration: [TRANSFER_MIGRATION.md](TRANSFER_MIGRATION.md)
- Implementation: [TRANSFER_IMPLEMENTATION.md](TRANSFER_IMPLEMENTATION.md)

**Logs:**

- Application logs: `logs/` directory
- Database logs: Check database configuration

**Testing:**

- Run test suite to verify functionality
- Check for errors in logs

---

**Version:** 1.0.0  
**Status:** Production Ready ✅
