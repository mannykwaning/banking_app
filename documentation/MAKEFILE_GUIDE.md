# Makefile Quick Reference

Quick reference for common Makefile commands in the Banking App API project.

## Getting Started

View all available commands:

```bash
make help
```

Show project information:

```bash
make info
```

Check status:

```bash
make status
```

## Local Development Workflow

### Initial Setup

```bash
# Create virtual environment
make venv

# Activate virtual environment
source banking_env/bin/activate

# Install dependencies
make install
```

### Running Locally

```bash
# Development mode (hot-reload enabled)
make dev

# Production mode (local)
make prod-local
```

### Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration

# Generate coverage report
make test-cov

# Generate detailed coverage reports to files
make test-cov-report
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Format and lint
make check
```

## Docker Development Workflow

### Development Mode

```bash
# Build and run (foreground)
make docker-dev

# Build and run (background)
make docker-dev-d

# View logs
make logs

# Stop containers
make docker-stop

# Restart containers
make docker-restart
```

### Production Mode

```bash
# Setup production environment (checks .env.production)
make prod-setup

# Build and run production
make docker-prod

# Build and run production (background)
make docker-prod-d

# View production logs
make logs-prod
```

### Container Management

```bash
# Open shell in container
make shell

# Stop containers
make docker-stop

# Stop and remove containers
make docker-down

# Remove everything (containers, volumes, images)
make docker-clean
```

## Database Management

```bash
# Remove database file
make db-clean

# Reset database (remove and recreate on next start)
make db-reset
```

## Health Checks & Monitoring

```bash
# Check API health
make health

# Check API readiness (with DB)
make health-ready

# Open API documentation
make docs
```

Example output:

```json
{
  "status": "healthy",
  "service": "Banking App API (Dev)"
}
```

## Cleanup

```bash
# Clean generated files (__pycache__, .pyc, etc.)
make clean

# Clean everything (Docker, DB, generated files)
make clean-all
```

## Common Workflows

### Starting Development

```bash
# Option 1: Local development
make install
make dev

# Option 2: Docker development
make docker-dev-d
make logs
```

### Running Tests

```bash
# Quick test run
make test

# Full test with coverage
make test-cov

# Generate coverage reports
make test-cov-report
```

### Before Committing Code

```bash
# Format and lint code
make check

# Run all tests
make test

# Check coverage
make test-cov
```

### Deploying to Production

```bash
# Check production setup
make prod-setup

# Build and deploy
make docker-prod-d

# Check status
make status

# Monitor logs
make logs-prod

# Check health
make health-ready
```

### Troubleshooting

#### Reset Everything

```bash
# Clean everything and start fresh
make clean-all
make docker-dev-d
```

#### Database Issues

```bash
# Remove and recreate database
make db-clean
make docker-restart
```

#### Container Issues

```bash
# Stop and rebuild containers
make docker-down
make docker-dev-d
```

#### View Container Logs

```bash
# Development logs
make logs

# Production logs
make logs-prod

# Or use status to check container state
make status
```

## Testing Workflows

### Quick Test

```bash
make test
```

### Test Specific Components

```bash
# Unit tests only (fast)
make test-unit

# Integration tests only
make test-integration
```

### Test with Coverage Analysis

```bash
# Generate HTML coverage report
make test-cov

# Generate text coverage reports
make test-cov-report

# View results
cat COVERAGE_SUMMARY.txt
open htmlcov/index.html
```

### Continuous Testing (Watch Mode)

```bash
# Requires pytest-watch
pip install pytest-watch

# Run tests on file changes
make test-watch
```

## Production Checklist

Before deploying to production:

- [ ] `make prod-setup` - Verify production config
- [ ] `make test-cov` - Ensure high test coverage (>90%)
- [ ] `make check` - Format and lint code
- [ ] Update `.env.production` with strong `SECRET_KEY`
- [ ] `make docker-prod-d` - Deploy in background
- [ ] `make health-ready` - Verify API is ready
- [ ] `make logs-prod` - Monitor startup logs
- [ ] `make graceful-shutdown-test` - Test shutdown behavior

## Quick Reference Table

| Command | Description | Use Case |
|---------|-------------|----------|
| `make dev` | Run locally | Local development |
| `make docker-dev-d` | Run in Docker (bg) | Docker development |
| `make test` | Run all tests | Quick validation |
| `make test-cov` | Test with coverage | Before commit |
| `make health` | Check health | Verify API is up |
| `make logs` | View logs | Debug issues |
| `make clean` | Clean files | Free up space |
| `make status` | Show status | Check containers |
| `make help` | Show all commands | Find a command |

## Environment Variables

The Makefile respects these environment variables:

- `ENVIRONMENT` - Set to `development`, `test`, or `production`

Example:

```bash
# Force production mode
export ENVIRONMENT=production
make prod-local
```

## Tips & Best Practices

1. **Always use `make help`** to discover available commands
2. **Use `make status`** to check container and service state
3. **Run `make test-cov`** before committing code
4. **Use `make docker-dev-d`** for background development
5. **Run `make clean`** periodically to free up space
6. **Use `make logs`** to debug container issues
7. **Run `make health-ready`** to verify DB connectivity

## Troubleshooting Guide

### "Command not found: make"

Install make:

```bash
# Ubuntu/Debian
sudo apt-get install make

# macOS
xcode-select --install
```

### "Docker daemon not running"

Start Docker:

```bash
sudo systemctl start docker  # Linux
# or start Docker Desktop
```

### "Permission denied" errors

Add user to docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Tests failing after changes

Clean and rebuild:

```bash
make clean
make db-clean
make test
```

## Additional Resources

- Run `make help` for complete command list
- See `README.md` for detailed setup instructions
- See `documentation/` for feature-specific guides
- See `COVERAGE_SUMMARY.txt` for test coverage details
- See `.env.example` for configuration options
