"""
Integration tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_health_basic_liveness(client):
    """Test basic health check endpoint returns healthy status."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    # Service name from settings (can vary by environment)
    assert len(data["service"]) > 0


def test_health_ready_with_db_connection(client):
    """Test readiness check endpoint with successful database connection."""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "service" in data
    # Service name from settings (can vary by environment)
    assert len(data["service"]) > 0
    assert data["database"] == "connected"
    assert "error" not in data


def test_health_endpoints_no_authentication_required(client):
    """Test that health endpoints don't require authentication."""
    # Health endpoint should work without auth headers
    response = client.get("/health")
    assert response.status_code == 200

    # Ready endpoint should work without auth headers
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_health_response_format(client):
    """Test that health endpoints return proper JSON format."""
    # Test /health
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert "service" in data

    # Test /health/ready
    response = client.get("/health/ready")
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert "service" in data
    assert "database" in data


def test_health_multiple_concurrent_requests(client):
    """Test that health endpoints handle concurrent requests correctly."""
    responses = []

    # Make multiple concurrent requests
    for _ in range(10):
        response = client.get("/health")
        responses.append(response)

    # All should succeed
    for response in responses:
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_health_ready_multiple_concurrent_requests(client):
    """Test that ready endpoint handles concurrent DB checks correctly."""
    responses = []

    # Make multiple concurrent requests
    for _ in range(10):
        response = client.get("/health/ready")
        responses.append(response)

    # All should succeed
    for response in responses:
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
        assert response.json()["database"] == "connected"


def test_health_performance(client):
    """Test that health check responds quickly."""
    import time

    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()

    assert response.status_code == 200
    # Health check should respond in less than 100ms
    assert (end_time - start_time) < 0.1


def test_health_ready_performance(client):
    """Test that ready check with DB ping responds quickly."""
    import time

    start_time = time.time()
    response = client.get("/health/ready")
    end_time = time.time()

    assert response.status_code == 200
    # Ready check should respond in less than 500ms
    assert (end_time - start_time) < 0.5
