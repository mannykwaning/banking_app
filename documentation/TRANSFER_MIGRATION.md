# Database Migration for Transfer Features

## Overview

This guide explains how to migrate the database schema to support the new money transfer features.

## Schema Changes

### Transaction Table Updates

The `transactions` table has been enhanced with the following new columns:

```sql
-- Transfer-specific fields
ALTER TABLE transactions ADD COLUMN transfer_type VARCHAR;
ALTER TABLE transactions ADD COLUMN destination_account_id INTEGER;
ALTER TABLE transactions ADD COLUMN external_account_number VARCHAR;
ALTER TABLE transactions ADD COLUMN external_bank_name VARCHAR;
ALTER TABLE transactions ADD COLUMN external_routing_number VARCHAR;

-- Status tracking fields
ALTER TABLE transactions ADD COLUMN status VARCHAR DEFAULT 'completed';
ALTER TABLE transactions ADD COLUMN reference_id VARCHAR;
ALTER TABLE transactions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add foreign key constraint
ALTER TABLE transactions ADD CONSTRAINT fk_destination_account 
    FOREIGN KEY (destination_account_id) REFERENCES accounts(id);

-- Add index on reference_id for faster lookups
CREATE INDEX idx_transactions_reference_id ON transactions(reference_id);
```

## Migration Steps

### Option 1: Fresh Database (Development)

If you're starting fresh or can recreate your development database:

```bash
# Activate virtual environment
source banking_env/bin/activate

# Remove existing database (if any)
rm -f banking_app.db

# Start the application (this will create tables with new schema)
uvicorn main:app --reload
```

### Option 2: Manual Migration (Production)

For existing databases with data:

1. **Backup your database first!**

   ```bash
   # For SQLite
   cp banking_app.db banking_app.db.backup
   
   # For PostgreSQL
   pg_dump -U postgres banking_db > backup_$(date +%Y%m%d).sql
   ```

2. **Apply schema changes:**

   **For SQLite:**

   ```bash
   sqlite3 banking_app.db << 'EOF'
   -- Add new columns
   ALTER TABLE transactions ADD COLUMN transfer_type VARCHAR;
   ALTER TABLE transactions ADD COLUMN destination_account_id INTEGER;
   ALTER TABLE transactions ADD COLUMN external_account_number VARCHAR;
   ALTER TABLE transactions ADD COLUMN external_bank_name VARCHAR;
   ALTER TABLE transactions ADD COLUMN external_routing_number VARCHAR;
   ALTER TABLE transactions ADD COLUMN status VARCHAR DEFAULT 'completed';
   ALTER TABLE transactions ADD COLUMN reference_id VARCHAR;
   ALTER TABLE transactions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
   
   -- Update existing records
   UPDATE transactions SET status = 'completed' WHERE status IS NULL;
   UPDATE transactions SET updated_at = created_at WHERE updated_at IS NULL;
   
   -- Create index
   CREATE INDEX IF NOT EXISTS idx_transactions_reference_id ON transactions(reference_id);
   EOF
   ```

   **For PostgreSQL:**

   ```sql
   -- Connect to database
   psql -U postgres -d banking_db
   
   -- Add new columns with defaults
   ALTER TABLE transactions ADD COLUMN IF NOT EXISTS transfer_type VARCHAR;
   ALTER TABLE transactions ADD COLUMN IF NOT EXISTS destination_account_id INTEGER;
   ALTER TABLE transactions ADD COLUMN IF NOT EXISTS external_account_number VARCHAR;
   ALTER TABLE transactions ADD COLUMN IF NOT EXISTS external_bank_name VARCHAR;
   ALTER TABLE transactions ADD COLUMN IF NOT EXISTS external_routing_number VARCHAR;
   ALTER TABLE transactions ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'completed';
   ALTER TABLE transactions ADD COLUMN IF NOT EXISTS reference_id VARCHAR;
   ALTER TABLE transactions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
   
   -- Add foreign key constraint
   ALTER TABLE transactions 
   ADD CONSTRAINT fk_destination_account 
   FOREIGN KEY (destination_account_id) 
   REFERENCES accounts(id)
   ON DELETE SET NULL;
   
   -- Create index
   CREATE INDEX IF NOT EXISTS idx_transactions_reference_id ON transactions(reference_id);
   
   -- Update existing records
   UPDATE transactions SET status = 'completed' WHERE status IS NULL;
   UPDATE transactions SET updated_at = created_at WHERE updated_at IS NULL;
   ```

### Option 3: Using Alembic (Recommended for Production)

If you want to use database migrations with Alembic:

1. **Install Alembic:**

   ```bash
   pip install alembic
   ```

2. **Initialize Alembic:**

   ```bash
   alembic init alembic
   ```

3. **Configure `alembic.ini`:**

   ```ini
   sqlalchemy.url = sqlite:///./banking_app.db
   ```

4. **Create migration:**

   ```bash
   alembic revision -m "add_transfer_fields_to_transactions"
   ```

5. **Edit the generated migration file** (`alembic/versions/xxx_add_transfer_fields.py`):

   ```python
   """add transfer fields to transactions
   
   Revision ID: xxx
   """
   from alembic import op
   import sqlalchemy as sa
   
   def upgrade():
       # Add new columns
       op.add_column('transactions', sa.Column('transfer_type', sa.String(), nullable=True))
       op.add_column('transactions', sa.Column('destination_account_id', sa.Integer(), nullable=True))
       op.add_column('transactions', sa.Column('external_account_number', sa.String(), nullable=True))
       op.add_column('transactions', sa.Column('external_bank_name', sa.String(), nullable=True))
       op.add_column('transactions', sa.Column('external_routing_number', sa.String(), nullable=True))
       op.add_column('transactions', sa.Column('status', sa.String(), nullable=False, server_default='completed'))
       op.add_column('transactions', sa.Column('reference_id', sa.String(), nullable=True))
       op.add_column('transactions', sa.Column('updated_at', sa.DateTime(), nullable=True))
       
       # Add foreign key
       op.create_foreign_key('fk_destination_account', 'transactions', 'accounts', 
                           ['destination_account_id'], ['id'])
       
       # Add index
       op.create_index('idx_transactions_reference_id', 'transactions', ['reference_id'])
   
   def downgrade():
       op.drop_index('idx_transactions_reference_id', 'transactions')
       op.drop_constraint('fk_destination_account', 'transactions', type_='foreignkey')
       op.drop_column('transactions', 'updated_at')
       op.drop_column('transactions', 'reference_id')
       op.drop_column('transactions', 'status')
       op.drop_column('transactions', 'external_routing_number')
       op.drop_column('transactions', 'external_bank_name')
       op.drop_column('transactions', 'external_account_number')
       op.drop_column('transactions', 'destination_account_id')
       op.drop_column('transactions', 'transfer_type')
   ```

6. **Run migration:**

   ```bash
   alembic upgrade head
   ```

## Verification

After migration, verify the schema:

```bash
# For SQLite
sqlite3 banking_app.db ".schema transactions"

# For PostgreSQL
psql -U postgres -d banking_db -c "\d transactions"
```

Expected output should show all new columns.

## Testing After Migration

1. **Start the application:**

   ```bash
   uvicorn main:app --reload
   ```

2. **Check API documentation:**
   Open <http://localhost:8000/docs> and verify the new transfer endpoints appear.

3. **Test a transfer:**

   ```bash
   # Get auth token
   TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=password" | jq -r .access_token)
   
   # Create test accounts if needed
   # ... (create accounts first)
   
   # Test internal transfer
   curl -X POST http://localhost:8000/api/v1/transfers/internal \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "source_account_id": 1,
       "destination_account_id": 2,
       "amount": 10.00,
       "description": "Test transfer"
     }'
   ```

## Rollback Plan

If you need to rollback:

1. **Restore from backup:**

   ```bash
   # For SQLite
   cp banking_app.db.backup banking_app.db
   
   # For PostgreSQL
   psql -U postgres -d banking_db < backup_20260115.sql
   ```

2. **Or use Alembic downgrade:**

   ```bash
   alembic downgrade -1
   ```

## Data Migration (if needed)

If you have existing transactions that need to be categorized:

```sql
-- Mark all existing transactions as completed
UPDATE transactions 
SET status = 'completed' 
WHERE status IS NULL;

-- Set updated_at to match created_at for existing records
UPDATE transactions 
SET updated_at = created_at 
WHERE updated_at IS NULL;
```

## Configuration Updates

Add the following environment variables (optional, defaults provided):

```bash
# .env file
MAX_TRANSFER_AMOUNT=100000.0
DAILY_TRANSFER_LIMIT=500000.0
MIN_TRANSFER_AMOUNT=0.01
MAX_EXTERNAL_TRANSFER_AMOUNT=50000.0
MIN_ACCOUNT_BALANCE=0.0
```

## Troubleshooting

### Issue: Foreign key constraint fails

**Solution:** Ensure the `accounts` table exists and has an `id` primary key before adding the constraint.

### Issue: Column already exists

**Solution:** Check if migration was already applied. Drop columns manually if needed:

```sql
ALTER TABLE transactions DROP COLUMN transfer_type;
-- etc...
```

### Issue: Application won't start after migration

**Solution:**

1. Check logs for specific errors
2. Verify all columns were added successfully
3. Ensure models match database schema
4. Restart application server

## Support

For issues with migration, check:

1. Database logs
2. Application logs in `logs/` directory
3. SQLAlchemy query logs (enable with `echo=True` in database.py)

## Next Steps

After successful migration:

1. Run integration tests: `pytest tests/integration/test_transfers.py`
2. Monitor application logs for any errors
3. Test in staging environment before production deployment
4. Update API documentation if needed
5. Train users on new transfer features
