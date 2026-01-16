# Graceful Shutdown Handling

This document explains how the Banking App API implements graceful shutdown handling for production deployments.

## Overview

Graceful shutdown ensures that:

- In-flight requests are completed before shutdown
- Database connections are properly closed
- Resources are cleaned up appropriately
- No data loss or corruption occurs
- Monitoring systems are notified properly

## Implementation Details

### 1. Application Level (FastAPI Lifespan)

The application uses FastAPI's lifespan context manager to handle startup and shutdown:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application")
    create_tables()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Initiating graceful shutdown")
    engine.dispose()  # Close database connections
    logger.info("Application shutdown complete")
```

**Key Features:**

- Logs all startup and shutdown events
- Properly disposes database engine and connections
- Handles exceptions during cleanup
- Provides clear visibility into shutdown process

### 2. Uvicorn Configuration

The ASGI server (Uvicorn) is configured with proper timeout values:

```bash
uvicorn main:app \
  --timeout-graceful-shutdown 30 \
  --timeout-keep-alive 5
```

**Configuration Parameters:**

- `--timeout-graceful-shutdown 30`: Waits up to 30 seconds for active requests to complete
- `--timeout-keep-alive 5`: Keeps idle connections alive for 5 seconds

### 3. Docker Configuration

#### Dockerfile

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", 
     "--timeout-graceful-shutdown", "30", "--timeout-keep-alive", "5"]
```

#### Docker Compose

```yaml
services:
  banking-api:
    stop_signal: SIGTERM  # Send SIGTERM for graceful shutdown
    stop_grace_period: 45s  # Wait 45s before forcing SIGKILL
```

**Why 45 seconds?**

- 30s for Uvicorn to complete in-flight requests
- 10s for application cleanup (database, logging)
- 5s buffer for container cleanup

## Signal Handling

### Signal Flow

1. **SIGTERM sent** (from Docker, Kubernetes, or system)
   - Uvicorn receives signal
   - Stops accepting new connections
   - Waits for active requests (up to 30s)

2. **Application cleanup** (FastAPI lifespan)
   - Lifespan shutdown handler executes
   - Database connections closed
   - Resources cleaned up

3. **Process exits** gracefully
   - Exit code 0 (success)
   - All logs flushed

4. **If timeout exceeded**
   - After 45s, Docker sends SIGKILL
   - Forced termination

## Health Checks During Shutdown

### Health Endpoint Behavior

During graceful shutdown:

- `/health` - Returns 503 Service Unavailable once shutdown initiated
- `/health/ready` - Returns not_ready status

This allows load balancers and orchestrators to stop routing traffic.

## Best Practices

### 1. Request Timeout Configuration

Ensure client timeouts exceed the graceful shutdown period:

```
Client timeout > 45s (stop_grace_period)
```

### 2. Load Balancer Configuration

Configure load balancers to:

- Check `/health/ready` endpoint
- Respect 503 status codes
- Stop sending new requests when unhealthy

### 3. Database Connection Management

```python
# Use context managers for database sessions
with SessionLocal() as db:
    # perform operations
    pass  # connection automatically closed
```

### 4. Long-Running Operations

For operations taking > 30 seconds:

- Use background tasks or job queues
- Return 202 Accepted immediately
- Process asynchronously

## Testing Graceful Shutdown

### Local Testing

```bash
# Start the application
docker-compose up

# Send SIGTERM signal
docker-compose stop

# Check logs for graceful shutdown messages
docker-compose logs
```

Expected log output:

```
INFO: Initiating graceful shutdown
INFO: Waiting for application shutdown.
INFO: Database connections closed
INFO: Application shutdown complete.
```

### Testing Under Load

```bash
# Generate load
ab -n 1000 -c 10 http://localhost:8000/api/v1/accounts/

# In another terminal, trigger shutdown
docker-compose stop

# Verify no failed requests
```

## Kubernetes Deployment

For Kubernetes deployments, ensure:

```yaml
spec:
  containers:
  - name: banking-api
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 5"]
    terminationGracePeriodSeconds: 60
```

**Configuration:**

- `preStop` hook: 5s delay before SIGTERM
- `terminationGracePeriodSeconds`: 60s total (exceeds stop_grace_period)

This allows:

1. Load balancer to deregister (5s)
2. Application graceful shutdown (45s)
3. Buffer for cleanup (10s)

## Monitoring Shutdown

### Key Metrics

Monitor these metrics during shutdown:

- Active request count
- Database connection pool size
- Response times
- Error rates

### Logging

All shutdown events are logged at INFO level:

- "Initiating graceful shutdown"
- "Database connections closed"
- "Application shutdown complete"

Error events are logged at ERROR level:

- "Error during shutdown cleanup"

## Troubleshooting

### Issue: Container killed after 45 seconds

**Cause:** Requests taking longer than graceful shutdown timeout

**Solution:**

1. Increase `stop_grace_period` in docker-compose.yml
2. Increase `--timeout-graceful-shutdown` in Uvicorn
3. Optimize slow endpoints

### Issue: Database connection errors during shutdown

**Cause:** Database accessed after engine disposal

**Solution:**
Ensure all database operations complete before engine.dispose()

### Issue: Requests fail during shutdown

**Cause:** Load balancer still routing traffic

**Solution:**

- Implement `/health/ready` endpoint checks
- Configure proper health check intervals
- Add pre-stop delay in Kubernetes

## Production Checklist

- [x] Uvicorn configured with graceful shutdown timeout
- [x] Docker Compose uses SIGTERM signal
- [x] Stop grace period > graceful shutdown timeout
- [x] Lifespan handler closes database connections
- [x] Health checks implemented
- [x] Shutdown events logged
- [x] Error handling in cleanup code
- [ ] Load balancer health checks configured
- [ ] Monitoring alerts for shutdown events
- [ ] Runbook for shutdown issues

## References

- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [Uvicorn Settings](https://www.uvicorn.org/settings/)
- [Docker Compose Shutdown](https://docs.docker.com/compose/faq/#why-do-my-services-take-10-seconds-to-recreate-or-stop)
- [Kubernetes Termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
