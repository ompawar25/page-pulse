import fastapi.testclient
from main import app

client = fastapi.testclient.TestClient(app)

# 1. Happy Path Test
def test_valid_url():
    response = client.post("/api/audit", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "status_code" in data
    assert "title" in data

# 2. Failure Case 1: Invalid Domain
def test_invalid_url():
    response = client.post("/api/audit", json={"url": "https://thisdomaindoesnotexist12345.com"})
    assert response.status_code == 400

# 3. Failure Case 2: Non-HTML Response
def test_non_html_url():
    response = client.post("/api/audit", json={"url": "https://via.placeholder.com/150"})
    assert response.status_code == 400