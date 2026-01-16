# Environment Configuration Quick Reference

## 🚀 Quick Start Commands

### Development

```bash
# Export environment variable
export ENVIRONMENT=development

# Run app
uvicorn main:app --reload

# Or one-liner
ENVIRONMENT=development uvicorn main:app --reload

# Docker
docker-compose -f docker-compose.dev.yml up
```

### Test

```bash
# Run tests
ENVIRONMENT=test pytest

# With coverage
ENVIRONMENT=test pytest --cov=app tests/
```

### Production

```bash
# Export environment variable
export ENVIRONMENT=production

# Run app
uvicorn main:app --host 0.0.0.0 --port 8000

# Docker
docker-compose up
```

## 📁 Environment Files

| File | Purpose | Debug | API Docs | CORS |
|------|---------|-------|----------|------|
| `.env.development` | Local dev | ✅ ON | ✅ ON | Permissive |
| `.env.test` | Testing | ❌ OFF | ❌ OFF | Restricted |
| `.env.production` | Production | ❌ OFF | ❌ OFF | Strict |

## ⚙️ Key Settings per Environment

### Development

```bash
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./data/banking_dev.db
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### Test

```bash
ENVIRONMENT=test
DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=sqlite:///:memory:
CORS_ORIGINS=["http://localhost:3000"]
```

### Production

```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/banking_prod.db
SECRET_KEY=<STRONG-KEY-HERE>
CORS_ORIGINS=["https://yourdomain.com"]
```

## 🔐 Security Checklist

### Before Production Deployment

- [ ] Generate strong `SECRET_KEY` (32+ characters)
- [ ] Set `DEBUG=False`
- [ ] Configure strict CORS origins
- [ ] Use proper database (PostgreSQL/MySQL)
- [ ] Set `LOG_LEVEL=INFO` or `WARNING`
- [ ] Never commit `.env.production`
- [ ] Use environment variables or secrets manager
- [ ] Enable HTTPS only
- [ ] Review all configuration settings

## 🔍 Verify Configuration

```bash
# Check loaded environment
python -c "from app.core.config import settings; print(f'Env: {settings.environment}, Debug: {settings.debug}')"

# Check all settings
python -c "
from app.core.config import settings
print(f'Environment: {settings.environment}')
print(f'Debug: {settings.debug}')
print(f'Database: {settings.database_url}')
print(f'Log Level: {settings.log_level}')
print(f'CORS: {settings.cors_origins}')
"
```

## 🛠️ Generate Secret Key

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
```

## 🐳 Docker Commands

```bash
# Development (hot reload)
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose up --build

# Stop all
docker-compose down

# View logs
docker-compose logs -f

# Clean rebuild
docker-compose down -v
docker-compose up --build
```

## 📊 Features by Environment

| Feature | Development | Test | Production |
|---------|-------------|------|------------|
| Hot Reload | ✅ | ❌ | ❌ |
| Debug Mode | ✅ | ❌ | ❌ |
| API Docs | ✅ | ❌ | ❌ |
| Verbose Logs | ✅ | ❌ | ⚠️ Configurable |
| CORS | All Origins | Limited | Strict |
| Database | File | Memory | File/Remote |

## 🔗 URLs

- **Development**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs> (dev only)
- **ReDoc**: <http://localhost:8000/redoc> (dev only)
- **Health Check**: <http://localhost:8000/health>

## 📖 More Information

See [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) for detailed documentation.
