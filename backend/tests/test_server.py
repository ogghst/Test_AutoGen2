import pytest
from fastapi.testclient import TestClient
from backend.server import app, lifespan

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_create_session(client):
    response = client.post("/api/session")
    assert response.status_code == 200
    assert "session_id" in response.json()

def test_websocket_connection(client):
    response = client.post("/api/session")
    session_id = response.json()["session_id"]
    with client.websocket_connect(f"/ws/{session_id}") as websocket:
        websocket.close()

def test_get_project(client):
    response = client.post("/api/session")
    session_id = response.json()["session_id"]
    response = client.get(f"/api/session/{session_id}/project")
    assert response.status_code == 200
    assert response.json()["name"] == "New Project"
