import pytest
from pathlib import Path
from core.models import Contact
from core.contact_store import ContactStore


@pytest.fixture
def temp_store(tmp_path):
    data_file = tmp_path / "test_contacts.json"
    return ContactStore(data_file=data_file)


def test_store_operations(temp_store):
    assert len(temp_store.list_all()) == 0

    c1 = Contact(name="Alice Smith", email="alice@example.com", phone="1234567890", tags=["work"])
    temp_store.add(c1)
    assert len(temp_store.list_all()) == 1

    found = temp_store.find_by_email("alice@example.com")
    assert found is not None
    assert found.name == "Alice Smith"

    results = temp_store.find_by_name("alice")
    assert len(results) == 1
    assert results[0].email == "alice@example.com"

    results = temp_store.find_by_tag("work")
    assert len(results) == 1

    temp_store.update_by_email("alice@example.com", phone="9876543210", notes="Updated notes")
    updated = temp_store.find_by_email("alice@example.com")
    assert updated is not None
    assert updated.phone == "9876543210"
    assert updated.notes == "Updated notes"

    assert temp_store.delete_by_email("alice@example.com") is True
    assert len(temp_store.list_all()) == 0
