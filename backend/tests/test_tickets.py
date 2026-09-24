import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_ticket():
    response = client.post("/tickets", json={"customer_email":"test@example.com","category":"OTHER","subject":"Test","description":"Test ticket","priority":"LOW"})
    assert response.status_code == 201
    assert response.json()["ticket_number"].startswith("BD-")
    assert response.json()["status"] == "OPEN"

def test_status_change_creates_audit():
    created = client.post("/tickets", json={"customer_email":"audit@example.com","category":"ORDER","subject":"Audit","description":"Audit ticket"}).json()
    updated = client.patch(f"/tickets/{created['id']}", json={"status":"IN_PROGRESS"})
    assert updated.status_code == 200
    detail = client.get(f"/tickets/{created['id']}").json()
    assert any(event["event_type"] == "STATUS_CHANGED" and event["old_value"] == "OPEN" and event["new_value"] == "IN_PROGRESS" for event in detail["events"])

