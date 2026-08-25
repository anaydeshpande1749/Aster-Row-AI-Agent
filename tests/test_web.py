import pytest

from web.app import web_app


@pytest.fixture
def client():
    web_app.config.update({
        "TESTING": True
    })

    with web_app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200


def test_empty_question(client):
    response = client.post(
        "/ask",
        json={"question": ""}
    )

    assert response.status_code == 400
    assert "error" in response.json


def test_order_lookup(client):
    response = client.post(
        "/ask",
        json={
            "question": "Where is order ORD-1007?"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert "answer" in data
    assert "sources" in data
    assert "tool_used" in data
    assert "handoff" in data

    assert "ORD-1007" in data["answer"]
    assert "UPS" in data["answer"]


def test_order_followup_eta(client):
    # Start conversation
    response = client.post(
        "/ask",
        json={
            "question": "Where is order ORD-1007?"
        }
    )

    assert response.status_code == 200

    # Follow-up question
    response = client.post(
        "/ask",
        json={
            "question": "When should I receive it?"
        }
    )

    assert response.status_code == 200

    data = response.json

    assert "August 22, 2026" in data["answer"]
    assert data["tool_used"] is True