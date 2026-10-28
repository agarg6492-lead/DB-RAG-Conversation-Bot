import pytest
from fastapi.testclient import TestClient
from app import Question

client = TestClient(app)

def test_ask_endpoint():
    response = client.post("/ask", json={"question": "give Department Names of Development Groups"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "context_used" in data
