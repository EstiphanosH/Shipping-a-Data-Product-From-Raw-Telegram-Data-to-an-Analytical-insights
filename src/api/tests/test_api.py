import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

def test_top_products():
    response = client.get("/api/reports/top-products?limit=5")
    assert response.status_code == 200
    assert "products" in response.json()
    
def test_channel_activity():
    response = client.get("/api/channels/chemed/activity")
    assert response.status_code == 200
    assert "activity" in response.json()

def test_search_messages():
    response = client.get("/api/search/messages?query=paracetamol")
    assert response.status_code == 200
    assert isinstance(response.json(), list)