# Graceful Shutdown Quick Reference

## Configuration Summary

### Timeouts (in seconds)

| Component | Timeout | Purpose |
|-----------|---------|---------|
| Uvicorn graceful shutdown | 30s | Complete in-flight requests |
| Keep-alive timeout | 5s | Idle connection timeout |
| Docker stop grace period | 45s | Total time before SIGKILL |
| Kubernetes termination (recommended) | 60s | Total pod termination time |

### Signal Flow

```
1. SIGTERM sent
   ↓
2. Uvicorn stops accepting new requests (0s)
   ↓
3. Wait for active requests (0-30s)
   ↓
4. Application cleanup via lifespan (0-10s)
   ↓
5. Process exits (0s)
   ↓
6. If not done by 45s: SIGKILL
```

## File Locations

- **Dockerfile**: `CMD` with uvicorn timeouts
- **docker-compose.yml**: `stop_signal`, `stop_grace_period`
- **docker-compose.dev.yml**: `stop_signal`, `stop_grace_period`, `command`
- **main.py**: `lifespan()` async context manager

## Key Commands

### Start Application

```bash
# Production
docker-compose up -d

# Development
docker-compose -f docker-compose.dev.yml up
```

### Graceful Shutdown Test

```bash
# Send SIGTERM (graceful)
docker-compose stop

# Check logs for graceful shutdown messages
docker-compose logs | grep -i "shutdown"
```

### Force Kill (avoid in production)

```bash
# SIGKILL immediately
docker-compose kill
```

## Verification Checklist

- [x] Uvicorn configured: `--timeout-graceful-shutdown 30`
- [x] Uvicorn configured: `--timeout-keep-alive 5`
- [x] Docker Compose: `stop_signal: SIGTERM`
- [x] Docker Compose: `stop_grace_period: 45s`
- [x] Application lifespan: database cleanup
- [x] Application lifespan: error handling
- [x] Logging: shutdown events

## Expected Log Messages

**Startup:**

```
INFO: Starting application
INFO: Database tables created successfully
INFO: Application startup complete
```

**Shutdown:**

```
INFO: Initiating graceful shutdown
INFO: Waiting for application shutdown
INFO: Database connections closed
INFO: Application shutdown complete
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Container killed at 45s | Long-running requests | Increase timeouts or optimize |
| DB errors on shutdown | Connections not closed | Check lifespan handler |
| Requests fail during shutdown | Load balancer routing | Configure health checks |

## Health Check Integration

During shutdown:

- `/health` → 503 Service Unavailable (after shutdown initiated)
- `/health/ready` → `{"status": "not_ready"}` (after shutdown initiated)

This signals load balancers to stop routing traffic.

## Production Deployment Notes

1. **Load Balancer Health Checks**
   - Endpoint: `/health/ready`
   - Interval: 10s
   - Timeout: 5s
   - Unhealthy threshold: 2

2. **Kubernetes Configuration**

   ```yaml
   terminationGracePeriodSeconds: 60
   preStop:
     exec:
       command: ["/bin/sh", "-c", "sleep 5"]
   ```

3. **Monitoring Alerts**
   - Alert on shutdown duration > 40s
   - Alert on forced SIGKILL
   - Track graceful vs forced shutdowns

## Testing

```bash
# Test graceful shutdown under load
ab -n 1000 -c 10 http://localhost:8000/health/ &
sleep 2
docker-compose stop
# Verify: no failed requests
```

## Documentation

Full details: [GRACEFUL_SHUTDOWN.md](GRACEFUL_SHUTDOWN.md)
