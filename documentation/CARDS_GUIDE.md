# Card Management Guide

This guide provides comprehensive documentation for the Card Management functionality in the Banking App API.

## Overview

The Card Management system allows you to issue, manage, and secure bank cards linked to accounts. It includes:

- **Multiple card types**: Debit, Credit, and Prepaid cards
- **Encryption**: Sensitive data (PAN, CVV) is encrypted using Fernet symmetric encryption
- **Security**: Only last 4 digits stored unencrypted, full PAN and CVV always encrypted at rest
- **Card limits**: Maximum 5 active cards per account
- **Status management**: Active, Inactive, Blocked, and Expired statuses
- **Luhn validation**: Generated card numbers pass the Luhn algorithm check

## Features

### 🔐 Security

- **Fernet Encryption**: Uses `cryptography` library with SHA256-derived keys
- **Encrypted Fields**: PAN (Primary Account Number) and CVV are always encrypted
- **Key Derivation**: Encryption key derived from application `SECRET_KEY`
- **Secure Access**: Full card details require authentication and explicit API call

### 💳 Card Types

- **Debit Cards**: Linked to checking/savings accounts
- **Credit Cards**: For credit-based transactions
- **Prepaid Cards**: Pre-loaded with funds

### 📊 Card Status

- **Active**: Card is active and can be used
- **Inactive**: Card temporarily deactivated
- **Blocked**: Card blocked for security reasons
- **Expired**: Card has passed expiration date

## Card Issuance Workflow

The card issuance follows a secure workflow:

```
Issue Card Request → Validate Account → Generate Card Details → Store Encrypted
```

### Step-by-Step Process

1. **Request Validation**
   - Verify account exists
   - Check account hasn't reached card limit (5 cards)
   - Validate cardholder name format

2. **Card Generation**
   - Generate 16-digit card number with Luhn check digit
   - Use test BIN `400000` (Visa test range)
   - Generate 3-digit CVV
   - Calculate expiry date (3 years from issuance)

3. **Encryption & Storage**
   - Encrypt full PAN using Fernet
   - Encrypt CVV using Fernet
   - Store only last 4 digits unencrypted
   - Save card with ACTIVE status

## API Endpoints

All card endpoints require authentication. Include your JWT token in the `Authorization` header.

### Issue a New Card

**POST** `/api/v1/cards`

Issue a new card for an existing account.

**Request Body:**

```json
{
  "account_id": 1,
  "cardholder_name": "JOHN DOE",
  "card_type": "debit"
}
```

**Response:** `201 Created`

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

**Business Rules:**

- Account must exist
- Maximum 5 active cards per account
- Cardholder name max 26 characters (standard card limit)
- Name automatically converted to uppercase

---

### List All Cards

**GET** `/api/v1/cards?skip=0&limit=100`

Get a paginated list of all cards.

**Response:** `200 OK`

```json
[
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
]
```

---

### Get Card by ID

**GET** `/api/v1/cards/{card_id}`

Get card information without sensitive data.

**Response:** `200 OK`

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

**Error Responses:**

- `404 Not Found`: Card doesn't exist

---

### Get Full Card Details (Sensitive)

**GET** `/api/v1/cards/{card_id}/details`

⚠️ **WARNING**: Returns decrypted PAN and CVV. Use only for authorized operations.

**Response:** `200 OK`

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

**Security Notes:**

- This endpoint is logged with WARNING level
- Only use when absolutely necessary
- Implement additional authorization checks in production
- Consider rate limiting this endpoint

---

### Get Masked Card Number

**GET** `/api/v1/cards/{card_id}/masked`

Get card number in masked format for display purposes.

**Response:** `200 OK`

```json
{
  "masked_number": "****-****-****-1234"
}
```

---

### Get Cards by Account

**GET** `/api/v1/cards/account/{account_id}`

Get all cards linked to a specific account.

**Response:** `200 OK`

```json
[
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
]
```

**Error Responses:**

- `404 Not Found`: Account doesn't exist

---

### Update Card Status

**PATCH** `/api/v1/cards/{card_id}/status`

Update the status of a card.

**Request Body:**

```json
{
  "status": "inactive"
}
```

**Valid Status Values:**

- `active`: Card is active and can be used
- `inactive`: Card temporarily deactivated
- `blocked`: Card blocked for security
- `expired`: Card has expired

**Response:** `200 OK`

```json
{
  "id": 1,
  "account_id": 1,
  "card_number_last4": "1234",
  "cardholder_name": "JOHN DOE",
  "card_type": "debit",
  "status": "inactive",
  "expiry_month": 12,
  "expiry_year": 2029,
  "issued_at": "2026-01-15T10:30:00",
  "created_at": "2026-01-15T10:30:00",
  "updated_at": "2026-01-15T10:30:00"
}
```

---

### Block a Card

**POST** `/api/v1/cards/{card_id}/block`

Block a card (convenience method for security operations).

**Response:** `200 OK`

```json
{
  "id": 1,
  "account_id": 1,
  "card_number_last4": "1234",
  "cardholder_name": "JOHN DOE",
  "card_type": "debit",
  "status": "blocked",
  "expiry_month": 12,
  "expiry_year": 2029,
  "issued_at": "2026-01-15T10:30:00",
  "created_at": "2026-01-15T10:30:00",
  "updated_at": "2026-01-15T10:30:00"
}
```

**Use Cases:**

- Lost or stolen card
- Suspicious activity detected
- Cardholder request

---

### Activate a Card

**POST** `/api/v1/cards/{card_id}/activate`

Activate a card (convenience method).

**Response:** `200 OK`

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

## Example Workflows

### Complete Card Issuance Flow

```bash
# 1. Create an account (if not exists)
curl -X POST "http://localhost:8000/api/v1/accounts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "account_holder": "John Doe",
    "account_type": "checking",
    "initial_balance": 1000.0
  }'

# Response: {"id": 1, "account_number": "1234567890", ...}

# 2. Issue a debit card
curl -X POST "http://localhost:8000/api/v1/cards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "account_id": 1,
    "cardholder_name": "JOHN DOE",
    "card_type": "debit"
  }'

# Response: {"id": 1, "card_number_last4": "1234", "status": "active", ...}

# 3. Get masked card number for display
curl -X GET "http://localhost:8000/api/v1/cards/1/masked" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response: {"masked_number": "****-****-****-1234"}
```

### Card Security Operations

```bash
# Block a card (e.g., card reported lost)
curl -X POST "http://localhost:8000/api/v1/cards/1/block" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Later, activate replacement card
curl -X POST "http://localhost:8000/api/v1/cards/2/activate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Managing Multiple Cards

```bash
# Issue multiple card types
curl -X POST "http://localhost:8000/api/v1/cards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "account_id": 1,
    "cardholder_name": "JOHN DOE",
    "card_type": "credit"
  }'

curl -X POST "http://localhost:8000/api/v1/cards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "account_id": 1,
    "cardholder_name": "JOHN DOE",
    "card_type": "prepaid"
  }'

# Get all cards for the account
curl -X GET "http://localhost:8000/api/v1/cards/account/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Database Schema

### Cards Table

```sql
CREATE TABLE cards (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL,
    card_number_last4 VARCHAR NOT NULL,
    encrypted_pan VARCHAR NOT NULL,      -- Encrypted full card number
    encrypted_cvv VARCHAR NOT NULL,      -- Encrypted CVV
    cardholder_name VARCHAR NOT NULL,
    card_type VARCHAR NOT NULL,          -- debit, credit, prepaid
    status VARCHAR NOT NULL,             -- active, inactive, blocked, expired
    expiry_month INTEGER NOT NULL,
    expiry_year INTEGER NOT NULL,
    issued_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

## Security Best Practices

### 1. Encryption

- **Never store PAN or CVV in plain text**
- Encryption key derived from `SECRET_KEY` in configuration
- Use strong `SECRET_KEY` in production (64+ characters)
- Consider key rotation strategy for production

### 2. Access Control

- Require authentication for all card endpoints
- Log all access to sensitive endpoints (`/details`)
- Implement rate limiting on sensitive operations
- Consider additional authorization checks in production

### 3. PCI DSS Considerations

For production environments handling real card data:

- **PCI DSS Compliance**: This implementation is for educational purposes
- **Use tokenization**: Consider services like Stripe, Square for real card processing
- **Never log sensitive data**: Ensure PAN/CVV never appear in logs
- **Secure transmission**: Always use HTTPS
- **Access auditing**: Track who accesses card details and when

### 4. Testing

The test BIN `400000` (Visa test range) is used for generated cards. For production:

- Integrate with actual card issuer APIs
- Use real BIN ranges assigned to your institution
- Implement additional fraud detection

## Error Handling

### Common Error Responses

**404 Not Found**

```json
{
  "detail": "Card with ID 999 not found"
}
```

**400 Bad Request**

```json
{
  "detail": "Account has reached maximum number of active cards (5)"
}
```

**422 Validation Error**

```json
{
  "detail": [
    {
      "loc": ["body", "cardholder_name"],
      "msg": "ensure this value has at most 26 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

## Testing

Comprehensive test suites are included:

### Unit Tests

- `tests/unit/test_encryption.py` - Encryption utilities (9 tests)
- `tests/unit/test_card_repository.py` - Data access layer (8 tests)
- `tests/unit/test_card_service.py` - Business logic (17 tests)

### Integration Tests

- `tests/integration/test_cards.py` - API endpoints (16 tests)

**Run all card tests:**

```bash
pytest tests/unit/test_card*.py tests/unit/test_encryption.py tests/integration/test_cards.py -v
```

**Total: 50 tests covering all card functionality**

## Architecture

The card system follows clean architecture principles:

```
API Layer (cards.py)
    ↓
Service Layer (card_service.py)
    ↓
Repository Layer (card_repository.py)
    ↓
Model Layer (card.py)
```

**Benefits:**

- Clear separation of concerns
- Easy to test
- Business logic isolated from data access
- Encryption handled transparently in service layer

## Limitations & Future Enhancements

### Current Limitations

- Test BIN only (not real card processor integration)
- No EMV chip data
- No PIN management
- No transaction authorization
- Single encryption key (no key rotation)

### Potential Enhancements

1. **Card Networks**: Integration with Visa, Mastercard, etc.
2. **3D Secure**: Authentication for online transactions
3. **Virtual Cards**: Generate temporary card numbers
4. **Card Controls**: Spending limits, merchant restrictions
5. **Notifications**: Real-time alerts for card usage
6. **Card Delivery**: Track physical card shipping
7. **PIN Management**: Set and reset card PINs
8. **Freeze/Unfreeze**: Temporary card suspension

## Support

For issues or questions:

- Check API documentation at `/docs`
- Review test cases for usage examples
- See main README for authentication guide

---

**Last Updated**: January 15, 2026  
**Version**: 1.0.0
