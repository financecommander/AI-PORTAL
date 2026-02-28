"""Tests for persistent conversation history routes."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup_db():
    """Ensure all tables are created and clean before each conversation test."""
    from backend.database import init_db, get_session, engine
    from backend.models import Conversation, ConversationMessage
    from sqlmodel import Session, delete

    init_db()

    # Clean up conversation tables between tests
    with Session(engine) as session:
        session.exec(delete(ConversationMessage))  # type: ignore[call-overload]
        session.exec(delete(Conversation))  # type: ignore[call-overload]
        session.commit()
    yield


def test_list_conversations_empty(client: TestClient, auth_headers: dict):
    """New user has no conversations."""
    response = client.get("/conversations/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_conversations_no_auth(client: TestClient):
    """Listing conversations without auth returns 403 or 401."""
    response = client.get("/conversations/")
    assert response.status_code in (401, 403)


def test_create_conversation(client: TestClient, auth_headers: dict):
    """Create a new conversation."""
    response = client.post(
        "/conversations/",
        json={"title": "My first chat"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My first chat"
    assert "conversation_id" in data
    assert data["messages"] == []


def test_create_conversation_defaults(client: TestClient, auth_headers: dict):
    """Create a conversation with default title."""
    response = client.post("/conversations/", json={}, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["title"] == "New Conversation"


def test_get_conversation_not_found(client: TestClient, auth_headers: dict):
    """Getting a non-existent conversation returns 404."""
    response = client.get("/conversations/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404


def test_add_and_get_messages(client: TestClient, auth_headers: dict):
    """Adding messages persists them and updates the title."""
    # Create conversation
    conv = client.post(
        "/conversations/",
        json={"title": "New Conversation"},
        headers=auth_headers,
    ).json()
    cid = conv["conversation_id"]

    # Add messages
    add_resp = client.post(
        f"/conversations/{cid}/messages",
        json={"messages": [
            {"role": "user", "content": "What is a CMBS loan?"},
            {"role": "assistant", "content": "A CMBS loan is..."},
        ]},
        headers=auth_headers,
    )
    assert add_resp.status_code == 201
    data = add_resp.json()
    assert len(data["messages"]) == 2
    # Title should be updated from first user message
    assert "What is a CMBS loan?" in data["title"]

    # GET returns same messages
    get_resp = client.get(f"/conversations/{cid}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert len(get_resp.json()["messages"]) == 2


def test_add_messages_invalid_role(client: TestClient, auth_headers: dict):
    """Adding messages with invalid role returns 422."""
    conv = client.post("/conversations/", json={}, headers=auth_headers).json()
    cid = conv["conversation_id"]

    response = client.post(
        f"/conversations/{cid}/messages",
        json={"messages": [{"role": "system", "content": "inject"}]},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_delete_conversation(client: TestClient, auth_headers: dict):
    """Deleting a conversation removes it."""
    conv = client.post(
        "/conversations/",
        json={"title": "To be deleted"},
        headers=auth_headers,
    ).json()
    cid = conv["conversation_id"]

    del_resp = client.delete(f"/conversations/{cid}", headers=auth_headers)
    assert del_resp.status_code == 204

    get_resp = client.get(f"/conversations/{cid}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_delete_conversation_not_found(client: TestClient, auth_headers: dict):
    """Deleting a non-existent conversation returns 404."""
    response = client.delete("/conversations/does-not-exist", headers=auth_headers)
    assert response.status_code == 404


def test_conversation_isolation(client: TestClient):
    """Users cannot see each other's conversations."""
    from backend.auth.jwt_handler import create_access_token

    token_a = create_access_token({"sub": "user_a_hash"})
    token_b = create_access_token({"sub": "user_b_hash"})
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    conv = client.post(
        "/conversations/",
        json={"title": "User A secret"},
        headers=headers_a,
    ).json()
    cid = conv["conversation_id"]

    # User B cannot access User A's conversation
    response = client.get(f"/conversations/{cid}", headers=headers_b)
    assert response.status_code == 404

    # User B's list is empty
    list_resp = client.get("/conversations/", headers=headers_b)
    assert list_resp.json() == []


def test_list_conversations_sorted(client: TestClient, auth_headers: dict):
    """Conversations are returned most-recently-updated first."""
    client.post("/conversations/", json={"title": "First"}, headers=auth_headers)
    client.post("/conversations/", json={"title": "Second"}, headers=auth_headers)

    resp = client.get("/conversations/", headers=auth_headers)
    titles = [c["title"] for c in resp.json()]
    # "Second" was created last → should appear first
    assert titles[0] == "Second"
