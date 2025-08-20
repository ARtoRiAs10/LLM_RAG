from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to" in response.json()["message"]

# This is a very basic integration test. A full test suite would mock
# the database and service calls to test logic in isolation.
def test_upload_and_query_flow():
    # This test is more complex in a fully containerized setup
    # as it requires the dependent services (Chroma, Ollama) to be running and accessible.
    # For now, we ensure the endpoints exist and return correct status codes for valid/invalid requests.
    
    # Test query endpoint without any documents
    response = client.post("/api/v1/query", json={"query": "What is FastAPI?"})
    assert response.status_code == 200 # The endpoint should still work, even if context is empty
    assert "response" in response.json()