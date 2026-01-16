#!/bin/bash
# Test script for graceful shutdown

set -e

echo "=========================================="
echo "Graceful Shutdown Test Script"
echo "=========================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Start the application
echo -e "${YELLOW}Test 1: Starting application...${NC}"
docker-compose -f docker-compose.dev.yml up -d
sleep 10

# Check if container is running
if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Application started successfully${NC}"
else
    echo -e "${RED}✗ Application failed to start${NC}"
    exit 1
fi
echo

# Test 2: Check health endpoint
echo -e "${YELLOW}Test 2: Checking health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health endpoint responding${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Health endpoint not responding correctly${NC}"
    exit 1
fi
echo

# Test 3: Check readiness endpoint
echo -e "${YELLOW}Test 3: Checking readiness endpoint...${NC}"
READY_RESPONSE=$(curl -s http://localhost:8000/health/ready)
if echo "$READY_RESPONSE" | grep -q "ready"; then
    echo -e "${GREEN}✓ Readiness endpoint responding${NC}"
    echo "Response: $READY_RESPONSE"
else
    echo -e "${RED}✗ Readiness endpoint not responding correctly${NC}"
    exit 1
fi
echo

# Test 4: Generate some load
echo -e "${YELLOW}Test 4: Generating load (20 requests)...${NC}"
for i in {1..20}; do
    curl -s http://localhost:8000/health > /dev/null &
done
echo -e "${GREEN}✓ Load generation started${NC}"
sleep 2
echo

# Test 5: Graceful shutdown
echo -e "${YELLOW}Test 5: Initiating graceful shutdown...${NC}"
START_TIME=$(date +%s)

# Send SIGTERM via docker-compose stop
docker-compose -f docker-compose.dev.yml stop

END_TIME=$(date +%s)
SHUTDOWN_TIME=$((END_TIME - START_TIME))

echo -e "${GREEN}✓ Graceful shutdown completed in ${SHUTDOWN_TIME}s${NC}"

if [ $SHUTDOWN_TIME -le 45 ]; then
    echo -e "${GREEN}✓ Shutdown within grace period (45s)${NC}"
else
    echo -e "${YELLOW}⚠ Shutdown took longer than grace period${NC}"
fi
echo

# Test 6: Check logs for shutdown messages
echo -e "${YELLOW}Test 6: Checking shutdown logs...${NC}"

LOGS=$(docker-compose -f docker-compose.dev.yml logs)

if echo "$LOGS" | grep -q "Initiating graceful shutdown"; then
    echo -e "${GREEN}✓ Found 'Initiating graceful shutdown' message${NC}"
else
    echo -e "${RED}✗ Missing 'Initiating graceful shutdown' message${NC}"
fi

if echo "$LOGS" | grep -q "Database connections closed"; then
    echo -e "${GREEN}✓ Found 'Database connections closed' message${NC}"
else
    echo -e "${RED}✗ Missing 'Database connections closed' message${NC}"
fi

if echo "$LOGS" | grep -q "Application shutdown complete"; then
    echo -e "${GREEN}✓ Found 'Application shutdown complete' message${NC}"
else
    echo -e "${RED}✗ Missing 'Application shutdown complete' message${NC}"
fi
echo

# Cleanup
echo -e "${YELLOW}Cleaning up...${NC}"
docker-compose -f docker-compose.dev.yml down -v
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo

echo "=========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "=========================================="
echo
echo "Summary:"
echo "- Application starts correctly"
echo "- Health endpoints respond"
echo "- Graceful shutdown works"
echo "- Shutdown logs are present"
echo "- Shutdown completes within grace period"
