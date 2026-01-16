# Environment Configuration Guide

## Overview

The banking app backend supports multiple environment configurations (development, test, production) with different settings for each. This allows you to:

- Run with optimized settings for each environment
- Keep secrets separate per environment
- Easily switch between environments
- Configure CORS, logging, and debugging per environment

## Environment Files

### Available Environment Files

1. **`.env.development`** - Local development configuration
   - Debug mode enabled
   - Verbose logging (DEBUG level)
   - SQLite database in `data/` directory
   - CORS allows multiple local origins
   - API docs enabled

2. **`.env.test`** - Testing configuration
   - Debug mode disabled
   - Minimal logging (WARNING level)
   - In-memory SQLite database
   - Restricted CORS
   - API docs disabled

3. **`.env.production`** - Production configuration
   - Debug mode disabled
   - INFO level logging
   - Production database
   - Strict CORS settings
   - API docs disabled

4. **`.env.example`** - Template for creating new configurations

## How to Use

### Method 1: Using ENVIRONMENT Variable (Recommended)

The application automatically loads the correct environment file based on the `ENVIRONMENT` variable:

#### Local Development

```bash
# Set the environment
export ENVIRONMENT=development

# Run the application
uvicorn main:app --reload

# Or run directly
ENVIRONMENT=development uvicorn main:app --reload
```

#### Testing

```bash
# Set environment for tests
export ENVIRONMENT=test

# Run tests
pytest

# Or run directly
ENVIRONMENT=test pytest
```

#### Production

```bash
# Set the environment
export ENVIRONMENT=production

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8000

# Or with gunicorn
ENVIRONMENT=production gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Method 2: Using Docker Compose

Docker Compose files are already configured for each environment:

#### Development (with hot reload)

```bash
# Uses .env.development
docker-compose -f docker-compose.dev.yml up

# Or with rebuild
docker-compose -f docker-compose.dev.yml up --build
```

#### Production

```bash
# Uses .env.production
docker-compose up

# Or with rebuild
docker-compose up --build
```

### Method 3: Copy to .env (Fallback)

If no `ENVIRONMENT` variable is set, the app looks for a `.env` file:

```bash
# For development
cp .env.development .env

# For test
cp .env.test .env

# For production
cp .env.production .env

# Then run
uvicorn main:app --reload
```

## Environment-Specific Settings

### Development Environment

```bash
ENVIRONMENT=development
DATABASE_URL=sqlite:///./data/banking_dev.db
APP_NAME=Banking App API (Dev)
DEBUG=True
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://127.0.0.1:3000"]
```

**Features:**

- ✅ API documentation enabled at `/docs` and `/redoc`
- ✅ Hot reload enabled
- ✅ Detailed debug logging
- ✅ Permissive CORS for local development
- ✅ SQLite database file in local directory

**Best For:**

- Local development
- Debugging
- Testing new features

### Test Environment

```bash
ENVIRONMENT=test
DATABASE_URL=sqlite:///:memory:
APP_NAME=Banking App API (Test)
DEBUG=False
LOG_LEVEL=WARNING
CORS_ORIGINS=["http://localhost:3000"]
```

**Features:**

- ❌ API documentation disabled
- ✅ In-memory database (fast, isolated tests)
- ⚠️ Minimal logging (only warnings and errors)
- ✅ Restricted CORS
- ✅ No persistent data

**Best For:**

- Running unit tests
- Integration tests
- CI/CD pipelines

### Production Environment

```bash
ENVIRONMENT=production
DATABASE_URL=sqlite:///./data/banking_prod.db
APP_NAME=Banking App API
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=["https://yourdomain.com"]
```

**Features:**

- ❌ API documentation disabled (security)
- ❌ Debug mode disabled
- ✅ Production logging (INFO level)
- 🔒 Strict CORS (only specific domains)
- 🔒 Strong secret key required

**Best For:**

- Production deployment
- Staging environment
- Public-facing API

## Configuration Options

### Required Settings

| Setting | Description | Example |
|---------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development`, `test`, `production` |
| `DATABASE_URL` | Database connection string | `sqlite:///./data/banking.db` |
| `SECRET_KEY` | JWT signing key (32+ chars) | Generated with `secrets.token_hex(32)` |

### Optional Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `APP_NAME` | `Banking App API` | Application name |
| `APP_VERSION` | `1.0.0` | Application version |
| `DEBUG` | `True` | Enable debug mode |
| `API_V1_PREFIX` | `/api/v1` | API route prefix |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_DIR` | `logs` | Log file directory |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

## CORS Configuration

CORS (Cross-Origin Resource Sharing) settings are critical for security. Configure based on your environment:

### Development CORS

```bash
# Allow multiple local development servers
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://127.0.0.1:3000"]
```

### Production CORS

```bash
# Only allow your production domain(s)
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

### Disable CORS (not recommended)

```bash
# Allow all origins (only for development/testing)
CORS_ORIGINS=["*"]
```

## Security Best Practices

### Development

- ✅ Use different `SECRET_KEY` than production
- ✅ Enable debug mode for detailed errors
- ✅ Use verbose logging
- ⚠️ Never commit `.env.development` with real secrets

### Test

- ✅ Use unique `SECRET_KEY` for tests
- ✅ Use in-memory database
- ✅ Disable external connections
- ✅ Use minimal logging

### Production

- 🔒 **CRITICAL:** Use a strong, unique `SECRET_KEY`
- 🔒 Disable debug mode (`DEBUG=False`)
- 🔒 Restrict CORS to specific domains
- 🔒 Use proper database (PostgreSQL/MySQL recommended)
- 🔒 Never expose `.env.production` or commit to git
- 🔒 Use environment variables or secrets management
- 🔒 Rotate secrets regularly
- 🔒 Use HTTPS only

## Generating Secrets

### Secret Key Generation

```bash
# Python method
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL method
openssl rand -hex 32

# Example output (DO NOT USE THIS)
# 8f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        env:
          ENVIRONMENT: test
        run: |
          pytest --cov=app tests/
```

### Docker Production Deployment

```bash
# Build production image
docker build -t banking-app:latest .

# Run with production config
docker run -d \
  -p 8000:8000 \
  -v banking-data:/app/data \
  -v banking-logs:/app/logs \
  --env ENVIRONMENT=production \
  --env-file .env.production \
  --name banking-app \
  banking-app:latest
```

## Troubleshooting

### Environment not loading

**Problem:** Application uses wrong environment

**Solution:**

```bash
# Check which environment file exists
ls -la .env*

# Verify ENVIRONMENT variable is set
echo $ENVIRONMENT

# Check which file is being loaded
ENVIRONMENT=development python -c "from app.core.config import settings; print(f'Loaded: {settings.environment}, Debug: {settings.debug}')"
```

### CORS errors in browser

**Problem:** `Access-Control-Allow-Origin` errors

**Solution:**

```bash
# Check current CORS settings
python -c "from app.core.config import settings; print(settings.cors_origins)"

# Update CORS_ORIGINS in your .env file
# Make sure to use JSON array format:
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### Secret key not loading

**Problem:** Application generates random key each time

**Solution:**

```bash
# Generate a strong secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to your .env file
echo 'SECRET_KEY=your-generated-key-here' >> .env.development
```

### Database not persisting

**Problem:** Database resets on restart

**Solution:**

```bash
# Check DATABASE_URL in your .env file
# For persistent database, use file path:
DATABASE_URL=sqlite:///./data/banking.db

# NOT in-memory:
# DATABASE_URL=sqlite:///:memory:  # ❌ This is for tests only
```

## Checking Current Configuration

### View loaded settings

```bash
# Check all settings
python -c "
from app.core.config import settings
print(f'Environment: {settings.environment}')
print(f'Debug: {settings.debug}')
print(f'Database: {settings.database_url}')
print(f'Log Level: {settings.log_level}')
print(f'CORS Origins: {settings.cors_origins}')
"
```

### Test environment loading

```bash
# Test development
ENVIRONMENT=development python -c "from app.core.config import settings; print(settings.environment, settings.debug)"

# Test production
ENVIRONMENT=production python -c "from app.core.config import settings; print(settings.environment, settings.debug)"

# Test test
ENVIRONMENT=test python -c "from app.core.config import settings; print(settings.environment, settings.debug)"
```

## Quick Reference

### Command Cheat Sheet

```bash
# Development
ENVIRONMENT=development uvicorn main:app --reload

# Test
ENVIRONMENT=test pytest

# Production
ENVIRONMENT=production uvicorn main:app --host 0.0.0.0 --port 8000

# Docker Dev
docker-compose -f docker-compose.dev.yml up

# Docker Prod
docker-compose up

# Check config
python -c "from app.core.config import settings; print(settings.environment)"
```

### File Locations

```
banking_app_backend/
├── .env.example          # Template
├── .env.development      # Development config
├── .env.test            # Test config
├── .env.production      # Production config (create from template)
└── app/
    └── core/
        └── config.py    # Configuration logic
```

## Additional Resources

- [12-Factor App Config](https://12factor.net/config)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
