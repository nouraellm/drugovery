"""Tests for compound endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Get authentication token"""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    return response.json()["access_token"]


def test_create_compound(auth_token):
    """Test creating a compound"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/api/v1/compounds",
        json={
            "name": "Ethanol",
            "smiles": "CCO",
            "molecular_formula": "C2H6O"
        },
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Ethanol"


def test_list_compounds(auth_token):
    """Test listing compounds"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/v1/compounds", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
