import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.data.decode() == "Welcome!"

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"