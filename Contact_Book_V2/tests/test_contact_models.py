import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from core.contact_models import Contact


def test_valid_contact():
    contact = Contact(
        first_name="  john  ",
        last_name="  doe  ",
        email="john.doe@example.com",
        phone="(555) 123-4567",
        company="Tech Corp",
        notes="Met at conference",
    )
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.full_name() == "John Doe"
    assert contact.email == "john.doe@example.com"
    assert contact.phone == "(555) 123-4567"
    assert contact.company == "Tech Corp"
    assert contact.notes == "Met at conference"
    assert contact.display() == "John Doe <john.doe@example.com> at Tech Corp"


def test_invalid_email():
    with pytest.raises(ValidationError):
        Contact(first_name="John", last_name="Doe", email="not-an-email", phone="555-123-4567")


def test_invalid_phone():
    with pytest.raises(ValidationError):
        Contact(first_name="John", last_name="Doe", email="john@example.com", phone="123")


def test_future_last_contacted():
    future_time = datetime.now() + timedelta(days=1)
    with pytest.raises(ValidationError):
        Contact(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="555-123-4567",
            last_contacted=future_time,
        )
