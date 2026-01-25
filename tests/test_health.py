"""Tests for health check endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz_returns_ok(client: TestClient) -> None:
    """Test that /healthz returns status ok."""
    response = client.get("/healthz")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_healthz_response_structure(client: TestClient) -> None:
    """Test that /healthz response has correct structure."""
    response = client.get("/healthz")

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"status", "version"}
