import os
import tempfile
from pathlib import Path

# Configure before importing app: tests never use the developer's normal database.
_test_dir = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_test_dir.name) / 'test.db'}"
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client=TestClient(app)

def test_health():
    d=client.get("/health").json()
    assert d["status"] == "ok" and d["production_ready"] is False

def test_ticket_creates_alert_and_updates():
    r=client.post("/api/tickets", json={"customer":"Demo Customer","subject":"Printer is offline","priority":"urgent"})
    assert r.status_code==201, r.text
    ticket=r.json()
    assert ticket["status"]=="new"
    alerts=client.get("/api/alerts").json()
    assert alerts[0]["ticket_id"]==ticket["id"] and alerts[0]["acknowledged"] is False
    assert client.post(f"/api/alerts/{alerts[0]['id']}/acknowledge").json()["acknowledged"] is True
    updated=client.patch(f"/api/tickets/{ticket['id']}",json={"status":"resolved"})
    assert updated.json()["status"]=="resolved"

def test_manual_lead_and_reply_draft_not_sent():
    r=client.post("/api/leads", json={"source":"nextdoor_manual","locality":"Pearl","need":"Wi-Fi keeps disconnecting"})
    assert r.status_code==201
    draft=client.get(f"/api/leads/{r.json()['id']}/reply-draft").json()
    assert draft["requires_human_approval"] is True
    assert draft["generated_by"]=="template-not-ai"

def test_validation():
    assert client.post("/api/tickets",json={"customer":"X","subject":"Hi"}).status_code==422
    assert client.patch("/api/tickets/999999",json={"status":"resolved"}).status_code==404
