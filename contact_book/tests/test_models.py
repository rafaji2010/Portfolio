import pytest
from pydantic import ValidationError
from core.models import Contact


def test_valid_contact():
    contact = Contact(
        name="John Doe",
        email="john@example.com",
        phone="123-456-7890",
        tags=["friends", "work"],
        notes="Some note",
    )
    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"
    assert contact.phone == "123-456-7890"
    assert contact.tags == ["friends", "work"]
    assert contact.notes == "Some note"
    assert contact.created_at is not None


def test_invalid_name():
    with pytest.raises(ValidationError):
        Contact(name="   ", email="john@example.com", phone="1234567890")


def test_invalid_email():
    with pytest.raises(ValidationError):
        Contact(name="John", email="not-an-email", phone="1234567890")


def test_invalid_phone():
    with pytest.raises(ValidationError):
        Contact(name="John", email="john@example.com", phone="123")
