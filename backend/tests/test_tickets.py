import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make_ticket(email="test@example.com"):
    return client.post("/tickets", json={"customer_email": email, "category": "OTHER", "subject": "Test", "description": "Test ticket", "priority": "LOW"}).json()


def test_create_ticket():
    response = client.post("/tickets", json={"customer_email": "create@example.com", "category": "OTHER", "subject": "Test", "description": "Test ticket", "priority": "LOW"})
    assert response.status_code == 201
    assert response.json()["ticket_number"].startswith("BD-")
    assert response.json()["status"] == "OPEN"


def test_status_change_creates_audit():
    created = make_ticket("audit@example.com")
    updated = client.patch(f"/tickets/{created['id']}", json={"status": "IN_PROGRESS"})
    assert updated.status_code == 200
    detail = client.get(f"/tickets/{created['id']}").json()
    assert any(event["event_type"] == "STATUS_CHANGED" and event["old_value"] == "OPEN" and event["new_value"] == "IN_PROGRESS" for event in detail["events"])


def test_customer_cannot_see_or_create_internal_notes():
    created = make_ticket("privacy@example.com")
    note = client.post(f"/tickets/{created['id']}/messages?viewer=agent", json={"message": "Private note", "type": "INTERNAL_NOTE"})
    assert note.status_code == 201
    customer_view = client.get(f"/tickets/{created['id']}?viewer=customer").json()
    assert all(message["message_type"] != "INTERNAL_NOTE" for message in customer_view["messages"])
    blocked = client.post(f"/tickets/{created['id']}/messages?viewer=customer", json={"message": "Not allowed", "type": "INTERNAL_NOTE"})
    assert blocked.status_code == 403


def test_customer_reply_is_saved_and_public():
    created = make_ticket("reply@example.com")
    response = client.post(f"/tickets/{created['id']}/messages?viewer=customer", json={"message": "Here is more detail", "type": "CUSTOMER_REPLY", "sender_name": "Customer"})
    assert response.status_code == 201
    detail = client.get(f"/tickets/{created['id']}?viewer=customer").json()
    assert detail["messages"][-1]["message"] == "Here is more detail"


def test_websocket_saves_and_broadcasts_public_reply():
    created = make_ticket("socket@example.com")
    with client.websocket_connect(f"/ws/tickets/{created['id']}?viewer=customer") as websocket:
        websocket.send_json({"message": "Live reply", "type": "CUSTOMER_REPLY", "sender_name": "Customer"})
        event = websocket.receive_json()
    assert event["event"] == "new_message"
    assert event["data"]["message"] == "Live reply"
