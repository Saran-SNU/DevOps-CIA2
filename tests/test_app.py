import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_landing_page(client):
    """Test the main landing page route"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'DevOps CI/CD Pipeline' in response.data
    assert b'Flask Application' in response.data

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert b'status' in response.data
    assert b'healthy' in response.data

def test_app_runs():
    """Test that the app instance is created correctly"""
    assert app is not None
    assert app.name == 'app'

