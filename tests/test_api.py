import os
from fastapi import status

API_KEY = os.getenv("API_KEY", "test_key")

def test_health_check(client):
    """Test if /health returns 200 and DB status."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert "status" in json_data
    assert "db_connectivity" in json_data

def test_get_data_unauthorized(client):
    """Test that an INVALID API Key fails (Security Check)."""
    # We send a key, but it's WRONG. This triggers 401.
    headers = {"x-api-key": "wrong_secret_key"} 
    response = client.get("/data", headers=headers)
    assert response.status_code == 401 # Unauthorized

def test_get_data_missing_header(client):
    """Test that MISSING API Key fails validation."""
    # No headers sent. This triggers 422 (Unprocessable Entity).
    response = client.get("/data")
    assert response.status_code == 422 

def test_get_data_success(client):
    """Test fetching data with valid key."""
    # We send the CORRECT key mocked in our tests
    headers = {"x-api-key": API_KEY}
    response = client.get("/data?limit=5", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["limit"] == 5