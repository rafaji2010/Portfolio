"""JSON persistence store for contacts."""

import json
from pathlib import Path
from typing import Optional, Any
from core.models import Contact

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "contacts.json"


class ContactStore:
    def __init__(self, data_file: Path = DATA_FILE) -> None:
        self.data_file = data_file
        self._ensure_data_dir()
        self.contacts: list[Contact] = self._load()

    def _ensure_data_dir(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[Contact]:
        if not self.data_file.exists():
            return []
        with open(self.data_file, "r") as f:
            data = json.load(f)
            return [Contact.model_validate(c) for c in data]

    def _save(self) -> None:
        with open(self.data_file, "w") as f:
            json.dump([c.model_dump(mode="json") for c in self.contacts], f, indent=2)

    def add(self, contact: Contact) -> Contact:
        self.contacts.append(contact)
        self._save()
        return contact

    def list_all(self) -> list[Contact]:
        return self.contacts

    def find_by_name(self, name: str) -> list[Contact]:
        return [c for c in self.contacts if name.lower() in c.name.lower()]

    def find_by_tag(self, tag: str) -> list[Contact]:
        return [c for c in self.contacts if tag.lower() in [t.lower() for t in c.tags]]

    def find_by_email(self, email: str) -> Optional[Contact]:
        for c in self.contacts:
            if c.email.lower() == email.lower():
                return c
        return None

    def delete_by_email(self, email: str) -> bool:
        original = len(self.contacts)
        self.contacts = [c for c in self.contacts if c.email.lower() != email.lower()]
        if len(self.contacts) < original:
            self._save()
            return True
        return False

    def update_by_email(self, email: str, **kwargs: Any) -> bool:
        """Update contact fields by email. kwargs = fields to update."""
        contact = self.find_by_email(email)
        if not contact:
            return False

        # Build updated contact
        data = contact.model_dump(mode="json")
        data.update({k: v for k, v in kwargs.items() if v is not None})

        # Remove old, add new
        self.contacts = [c for c in self.contacts if c.email.lower() != email.lower()]
        self.contacts.append(Contact.model_validate(data))
        self._save()
        return True

    def clear_all(self) -> None:
        self.contacts = []
        self._save()
