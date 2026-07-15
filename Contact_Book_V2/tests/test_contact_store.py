import pytest
from pathlib import Path
from core.contact_models import Contact
from core.contact_store import ContactStore


@pytest.fixture
def temp_store():
    return ContactStore(max_recent=3)


def test_store_operations(temp_store, tmp_path):
    c1 = Contact(
        first_name="Alice", last_name="Brown", email="alice@example.com", phone="555-111-2222"
    )
    c2 = Contact(
        first_name="John", last_name="Doe", email="john.doe@example.com", phone="555-222-3333"
    )
    c3 = Contact(
        first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone="555-333-4444"
    )
    c4 = Contact(
        first_name="Bob", last_name="Doe", email="bob.doe@example.com", phone="555-444-5555"
    )

    temp_store.add_contact(c1)
    temp_store.add_contact(c2)
    temp_store.add_contact(c3)
    temp_store.add_contact(c4)

    assert len(temp_store) == 4

    assert temp_store.get_by_email("john.doe@example.com").first_name == "John"
    assert temp_store.get_by_email("unknown@example.com") is None

    ordered = temp_store.get_all_alphabetical()
    assert [c.full_name() for c in ordered] == ["Alice Brown", "Bob Doe", "John Doe", "Jane Smith"]

    suggestions = temp_store.autocomplete_name("jo")
    assert "john doe" in suggestions

    results = temp_store.search_by_name("jo")
    assert [c.full_name() for c in results] == ["John Doe"]

    # Record contact interactions
    temp_store.contact("alice@example.com")
    temp_store.contact("john.doe@example.com")
    temp_store.contact("jane.smith@example.com")

    recent = temp_store.get_recent_contacts(3)
    assert len(recent) == 3
    assert [c.full_name() for c in recent] == ["Jane Smith", "John Doe", "Alice Brown"]

    # Test persistence
    save_file = tmp_path / "contacts_test.json"
    temp_store.save(save_file)

    new_store = ContactStore()
    new_store.load(save_file)
    assert len(new_store) == 4
    assert new_store.get_by_email("alice@example.com").first_name == "Alice"
