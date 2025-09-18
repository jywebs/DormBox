"""Basic application tests."""
from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)

def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_box():
    """Test box creation."""
    response = client.post(
        "/api/v1/boxes",
        json={
            "name": "Test Box",
            "description": "Test description",
            "tags": ["test"],
            "status": "planned"
        },
        params={"workspace_id": "test-workspace"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Box"
    assert data["description"] == "Test description"
    assert data["tags"] == ["test"]
    assert data["status"] == "planned"
    assert "qrSlug" in data
    assert "id" in data

def test_create_item():
    """Test item creation."""
    # First create a box
    box_response = client.post(
        "/api/v1/boxes",
        json={
            "name": "Test Box",
            "status": "planned"
        },
        params={"workspace_id": "test-workspace"}
    )
    box_data = box_response.json()
    
    # Then create an item in that box
    response = client.post(
        "/api/v1/items",
        json={
            "title": "Test Item",
            "description": "Test description",
            "quantity": 1,
            "boxId": box_data["id"],
            "status": "planned"
        },
        params={"workspace_id": "test-workspace"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["description"] == "Test description"
    assert data["quantity"] == 1
    assert data["boxId"] == box_data["id"]
    assert data["status"] == "planned"
    assert "id" in data

def test_create_bundle():
    """Test bundle creation."""
    response = client.post(
        "/api/v1/bundles",
        json={
            "name": "Test Bundle",
            "description": "Test description",
            "tags": ["test"],
            "itemIds": []
        },
        params={"workspace_id": "test-workspace"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Bundle"
    assert data["description"] == "Test description"
    assert data["tags"] == ["test"]
    assert data["itemIds"] == []
    assert data["itemCount"] == 0
    assert "id" in data