import pytest
from pydantic import ValidationError

from app.schemas import SupportTicketCreate


def test_support_ticket_accepts_valid_payload():
    ticket = SupportTicketCreate(
        category="System Bug",
        subject="Login page error",
        description="The login button remains disabled after a failed request.",
    )
    assert ticket.category == "System Bug"


@pytest.mark.parametrize(
    "payload",
    [
        {"category": "Other", "subject": "Valid subject", "description": "Valid description"},
        {"category": "General Question", "subject": "x", "description": "Valid description"},
        {"category": "General Question", "subject": "Valid subject", "description": "short"},
    ],
)
def test_support_ticket_rejects_invalid_payload(payload):
    with pytest.raises(ValidationError):
        SupportTicketCreate(**payload)
