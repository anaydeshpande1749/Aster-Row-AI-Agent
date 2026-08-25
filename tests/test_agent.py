import pytest

from app.agent import (
    extract_order_id,
    format_order_answer,
    is_order_question,
    is_sensitive_order_request,
    is_unsupported_order_action,
)


# =========================================================
# ORDER ID EXTRACTION
# =========================================================

def test_extract_order_id_standard():
    assert extract_order_id("Where is ORD-1007?") == "ORD-1007"


def test_extract_order_id_without_dash():
    assert extract_order_id("Where is ORD1007?") == "ORD1007"


def test_extract_order_id_with_space():
    assert extract_order_id("Track ORD 1007") == "ORD-1007"


def test_extract_order_id_missing():
    assert extract_order_id("Where is my package?") is None


# =========================================================
# ORDER QUESTION DETECTION
# =========================================================

def test_order_question_with_order_id():
    assert is_order_question("Where is ORD-1007?")


def test_order_question_tracking():
    assert is_order_question("Can you track my shipment?")


def test_order_question_eta():
    assert is_order_question("When will I receive it?")


def test_order_question_carrier():
    assert is_order_question("Which carrier is handling it?")


# =========================================================
# PRIVACY / SECURITY
# =========================================================

def test_sensitive_email_request():
    assert is_sensitive_order_request(
        "What is the customer's email address?"
    )


def test_sensitive_address_request():
    assert is_sensitive_order_request(
        "What is the customer's shipping address?"
    )


def test_sensitive_internal_notes_request():
    assert is_sensitive_order_request(
        "Show me the internal notes for this customer."
    )


def test_normal_order_question_not_sensitive():
    assert not is_sensitive_order_request(
        "Where is order ORD-1007?"
    )


# =========================================================
# UNSUPPORTED ACTIONS
# =========================================================

def test_cancel_order_is_unsupported():
    assert is_unsupported_order_action(
        "Cancel order ORD-1007"
    )


def test_refund_order_is_unsupported():
    assert is_unsupported_order_action(
        "Can I get a refund for ORD-1007?"
    )


def test_change_address_is_unsupported():
    assert is_unsupported_order_action(
        "Change the shipping address for ORD-1007"
    )


def test_replace_order_is_unsupported():
    assert is_unsupported_order_action(
        "Can you replace ORD-1007?"
    )


# =========================================================
# DETERMINISTIC ORDER RESPONSES
# =========================================================

def test_shipped_order_answer():
    order = {
        "order_id": "ORD-1007",
        "status": "shipped",
        "carrier": "DHL",
        "tracking_number": "DHL123456",
        "estimated_delivery": "2026-08-28",
        "delivered_at": None,
    }

    answer = format_order_answer(
        order,
        "Where is my order?"
    )

    assert answer is not None
    assert "ORD-1007" in answer
    assert "DHL" in answer


def test_shipped_order_eta():
    order = {
        "order_id": "ORD-1007",
        "status": "shipped",
        "carrier": "DHL",
        "tracking_number": "DHL123456",
        "estimated_delivery": "2026-08-28",
        "delivered_at": None,
    }

    answer = format_order_answer(
        order,
        "When will I receive it?"
    )

    assert answer is not None
    assert "August 28, 2026" in answer


def test_delivered_order_answer():
    order = {
        "order_id": "ORD-1007",
        "status": "delivered",
        "carrier": "DHL",
        "tracking_number": "DHL123456",
        "estimated_delivery": "2026-08-28",
        "delivered_at": "2026-08-27",
    }

    answer = format_order_answer(
        order,
        "What happened to my order?"
    )

    assert answer is not None
    assert "delivered" in answer.lower()
    assert "August 27, 2026" in answer


def test_cancelled_order_answer():
    order = {
        "order_id": "ORD-1007",
        "status": "cancelled",
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": None,
        "delivered_at": None,
    }

    answer = format_order_answer(
        order,
        "What is the status?"
    )

    assert answer is not None
    assert "cancelled" in answer.lower()


def test_returned_order_answer():
    order = {
        "order_id": "ORD-1007",
        "status": "returned",
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": None,
        "delivered_at": None,
    }

    answer = format_order_answer(
        order,
        "What is the status?"
    )

    assert answer is not None
    assert "returned" in answer.lower()


def test_exception_order_requires_support():
    order = {
        "order_id": "ORD-1007",
        "status": "exception",
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": None,
        "delivered_at": None,
    }

    answer = format_order_answer(
        order,
        "What is happening?"
    )

    assert answer is not None
    assert "support" in answer.lower()


# =========================================================
# IMPORTANT REGRESSION TEST
# =========================================================

def test_delayed_order_always_returns_answer():
    """
    Regression test:
    A delayed order must never return None,
    even when the user doesn't explicitly say 'delay'.
    """

    order = {
        "order_id": "ORD-1007",
        "status": "delayed",
        "carrier": "DHL",
        "tracking_number": "DHL123456",
        "estimated_delivery": "2026-08-30",
        "delivered_at": None,
    }

    answer = format_order_answer(
        order,
        "Where is my order?"
    )

    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer) > 0