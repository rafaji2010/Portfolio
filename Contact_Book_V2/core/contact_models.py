"""
core/contact_models.py
Pydantic models for Contact Book
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr, Field


class Contact(BaseModel):
    """
    Contact model with validation.

    Features:
    - Email validation (uses Pydantic's EmailStr)
    - Phone number format validation
    - Name validation (non-empty)
    - Last contacted timestamp
    """

    first_name: str = Field(min_length=1, description="First name")
    last_name: str = Field(min_length=1, description="Last name")
    email: EmailStr = Field(description="Valid email address")
    phone: str = Field(description="Phone number")
    company: Optional[str] = None
    notes: Optional[str] = None
    last_contacted: datetime = Field(default_factory=datetime.now)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not empty and has no leading/trailing spaces."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty")
        return cleaned.title()  # Capitalize first letter of each word

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """
        Validate phone number format.
        Accepts: (123) 456-7890, 123-456-7890, 123.456.7890, +1 123 456 7890
        """
        # Remove common separators for validation
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Phone number cannot be empty")

        # Remove separators for length check
        digits = "".join(c for c in cleaned if c.isdigit())

        # Check length (US numbers: 10 digits, +1 = 11 digits)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Phone number must have 10-15 digits")

        return cleaned

    @field_validator("last_contacted")
    @classmethod
    def validate_last_contacted(cls, v: datetime) -> datetime:
        """Ensure last_contacted is not in the future."""
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.now()
        if v > now:
            raise ValueError("last_contacted cannot be in the future")
        return v

    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}"

    def display(self) -> str:
        """Return formatted display string."""
        company_str = f" at {self.company}" if self.company else ""
        return f"{self.full_name()} <{self.email}>{company_str}"

    def __repr__(self) -> str:
        return f"Contact({self.full_name()}, {self.email})"


if __name__ == "__main__":
    print("=== Contact Model Validation Demo ===")

    # Valid contact
    try:
        contact = Contact(
            first_name="  john  ",
            last_name="  doe  ",
            email="john.doe@example.com",
            phone="(555) 123-4567",
            company="Tech Corp",
            notes="Met at conference",
        )
        print(f"✅ Valid contact: {contact.display()}")
        print(f"  Full name: {contact.full_name()}")
        print(f"  Phone: {contact.phone}")
    except ValueError as e:
        print(f"❌ {e}")

    print("\n--- Testing Invalid Contacts ---")

    # Invalid email
    try:
        contact = Contact(
            first_name="Jane", last_name="Smith", email="not-an-email", phone="555-123-4567"
        )
    except ValueError as e:
        print(f"❌ Invalid email: {e}")

    # Invalid phone (too short)
    try:
        contact = Contact(
            first_name="Bob",
            last_name="Brown",
            email="bob@example.com",
            phone="123-456",  # Too short
        )
    except ValueError as e:
        print(f"❌ Invalid phone: {e}")

    # Empty first name
    try:
        contact = Contact(
            first_name="", last_name="Smith", email="smith@example.com", phone="555-123-4567"
        )
    except ValueError as e:
        print(f"❌ Empty name: {e}")
