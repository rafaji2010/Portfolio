"""
core/contact_store.py
Contact store with four indexes:
1. BST (by last name) → alphabetical listing
2. Trie → autocomplete by name
3. Hash Map (email → contact) → O(1) email lookup
4. Min-Heap → recent contacts tracking
"""

from __future__ import annotations

import heapq
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from core.contact_bst import ContactBST
from core.contact_models import Contact
from core.trie import Trie


class ContactStore:
    """
    Contact store with four indexes.

    All indexes stay in sync through add_contact.

    Indexes:
    1. BST (by last name) → O(log n) alphabetical listing
    2. Trie → O(m) autocomplete (m = prefix length)
    3. Hash Map → O(1) email lookup
    4. Min-Heap → O(log n) recent contacts tracking

    Example:
        >>> store = ContactStore()
        >>> contact = Contact(
        ...     first_name="John", last_name="Doe",
        ...     email="john@example.com", phone="555-1234"
        ... )
        >>> store.add_contact(contact)
        >>> store.get_by_email("john@example.com")
        Contact(John Doe, john@example.com)
        >>> store.autocomplete_name("jo")
        ['john doe']
        >>> store.get_recent_contacts(3)
        [Contact(John Doe, john@example.com), ...]
    """

    def __init__(self, max_recent: int = 10):
        """
        Initialize the contact store.

        Args:
            max_recent: Maximum number of recent contacts to track
        """
        self.max_recent = max_recent

        # Main storage - list of all contacts
        self._contacts: List[Contact] = []

        # Index 1: BST by last name (for alphabetical listing)
        self._bst: ContactBST = ContactBST()

        # Index 2: Trie for autocomplete (stores lowercase full names)
        self._name_trie: Trie = Trie()

        # Index 3: Hash Map email → contact index (O(1) lookup)
        self._email_index: dict[str, int] = {}

        # Index 4: Min-heap for recent contacts
        # Stores tuples: (timestamp, contact_index)
        self._recent_heap: List[Tuple[datetime, int]] = []
        self._recent_set: set[int] = set()  # Track which contacts are in heap

    def add_contact(self, contact: Contact) -> int:
        """
        Add a contact to the store.

        Updates all four indexes atomically.

        Time: O(log n) for BST + O(m) for Trie + O(1) for Hash Map + O(log n) for Heap
        Space: O(1) amortized

        Args:
            contact: Contact to add

        Returns:
            Index of the added/updated contact

        Raises:
            ValueError: If contact validation fails
        """
        # Check for duplicate email (keys are normalized to lowercase)
        email_key = contact.email.lower()
        if email_key in self._email_index:
            idx = self._email_index[email_key]
            self._update_contact(idx, contact)
            return idx

        # Add to main list
        idx = len(self._contacts)
        self._contacts.append(contact)

        # Index 1: BST (O(log n) average)
        self._bst.insert(contact)

        # Index 2: Trie (O(m) where m = name length)
        full_name = contact.full_name().lower()
        self._name_trie.insert(full_name)

        # Index 3: Hash Map (O(1)) — lowercase keys for case-insensitive lookup
        self._email_index[email_key] = idx

        # Index 4: Heap (O(log n))
        self._push_recent(idx)

        return idx

    def _update_contact(self, idx: int, new_contact: Contact) -> None:
        """
        Update an existing contact.

        This is more complex because we need to update all indexes.

        Args:
            idx: Index of contact to update
            new_contact: New contact data
        """
        old_contact = self._contacts[idx]

        # Update main list
        self._contacts[idx] = new_contact

        # If email changed, update hash map
        if old_contact.email.lower() != new_contact.email.lower():
            del self._email_index[old_contact.email.lower()]
            self._email_index[new_contact.email.lower()] = idx

        # BST update: rebuild if name changed
        if (
            old_contact.last_name != new_contact.last_name
            or old_contact.first_name != new_contact.first_name
        ):
            self._rebuild_bst()

        # Trie update: remove old name, add new
        if old_contact.full_name().lower() != new_contact.full_name().lower():
            old_name = old_contact.full_name().lower()
            new_name = new_contact.full_name().lower()
            self._name_trie.delete(old_name)
            self._name_trie.insert(new_name)

    def _rebuild_bst(self) -> None:
        """Rebuild BST from all contacts."""
        self._bst = ContactBST()
        for contact in self._contacts:
            self._bst.insert(contact)

    def _push_recent(self, idx: int) -> None:
        """
        Add contact to recent heap.

        Args:
            idx: Contact index to add
        """
        timestamp = datetime.now()
        heapq.heappush(self._recent_heap, (timestamp, idx))
        self._recent_set.add(idx)

        # Compact heap if too large (remove duplicates)
        if len(self._recent_heap) > self.max_recent * 2:
            self._compact_recent_heap()

    def _compact_recent_heap(self) -> None:
        """
        Remove duplicate entries from heap and keep only max_recent.

        This is called periodically to keep the heap size manageable.
        """
        # Keep only the most recent entry for each contact
        seen: set[int] = set()
        temp: List[Tuple[datetime, int]] = []

        # Sort by timestamp (most recent first)
        sorted_heap = sorted(self._recent_heap, key=lambda x: x[0], reverse=True)

        for timestamp, idx in sorted_heap:
            if idx not in seen:
                seen.add(idx)
                temp.append((timestamp, idx))
                if len(temp) == self.max_recent:
                    break

        # Reverse to maintain heap property (min-heap of timestamps)
        self._recent_heap = [(t, i) for t, i in reversed(temp)]
        self._recent_set = set(i for _, i in self._recent_heap)

    def get_by_email(self, email: str) -> Optional[Contact]:
        """
        Look up contact by email.

        Time: O(1) average

        Args:
            email: Email address to look up

        Returns:
            Contact if found, None otherwise
        """
        idx = self._email_index.get(email.lower())
        if idx is not None:
            return self._contacts[idx]
        return None

    def search_by_name(self, query: str) -> List[Contact]:
        """
        Search contacts by name (prefix match).

        Uses Trie for prefix matching and BST for ordered results.

        Time: O(m + k) where m = prefix length, k = matches
        Space: O(k)

        Args:
            query: Name prefix to search for

        Returns:
            List of matching contacts
        """
        results: List[Contact] = []
        query_lower = query.lower()

        # Get all names from Trie that start with the prefix
        matching_names = set(self._name_trie.starts_with(query_lower))

        # If no matches in Trie, return empty
        if not matching_names and query_lower:
            return []

        # Scan BST and collect matching contacts
        for contact in self._bst.inorder():
            full_name = contact.full_name().lower()
            # Check if name matches Trie results OR starts with query
            if full_name in matching_names or full_name.startswith(query_lower):
                results.append(contact)

        return results

    def autocomplete_name(self, prefix: str) -> List[str]:
        """
        Get name suggestions for autocomplete.

        Time: O(m + k) where m = prefix length, k = matches
        Space: O(k)

        Args:
            prefix: Name prefix to autocomplete

        Returns:
            List of full names matching the prefix
        """
        return self._name_trie.starts_with(prefix.lower())

    def get_all_alphabetical(self) -> List[Contact]:
        """
        Get all contacts in alphabetical order by last name.

        Time: O(n)
        Space: O(n)

        Returns:
            List of all contacts sorted alphabetically
        """
        return self._bst.to_list()

    def get_recent_contacts(self, n: Optional[int] = None) -> List[Contact]:
        """
        Get most recently contacted contacts.

        Time: O(k log k) where k = max_recent
        Space: O(k)

        Args:
            n: Number of contacts to return (default: max_recent)

        Returns:
            List of recent contacts (most recent first)
        """
        if n is None:
            n = self.max_recent

        if not self._recent_heap:
            return []

        # Compact heap first to remove duplicates
        self._compact_recent_heap()

        # Get top n entries (most recent)
        sorted_heap = sorted(self._recent_heap, key=lambda x: x[0], reverse=True)
        recent = sorted_heap[: min(n, len(sorted_heap))]

        return [self._contacts[idx] for _, idx in recent]

    def contact(self, email: str) -> Optional[Contact]:
        """
        Record that a contact was contacted.

        Updates the last_contacted timestamp and recent heap.

        Time: O(1) for lookup + O(log n) for heap

        Args:
            email: Email of the contact

        Returns:
            Updated contact if found, None otherwise
        """
        contact = self.get_by_email(email)
        if contact is None:
            return None

        # Update timestamp
        contact.last_contacted = datetime.now()

        # Update heap
        idx = self._email_index[email.lower()]
        self._push_recent(idx)

        return contact

    def save(self, path: Path) -> None:
        """
        Save all contacts to JSON file.

        Time: O(n)

        Args:
            path: Path to save the JSON file
        """
        data = [contact.model_dump(mode="json") for contact in self._contacts]
        path.write_text(json.dumps(data, indent=2, default=str))

    def load(self, path: Path) -> None:
        """
        Load contacts from JSON file.

        Resets all indexes before loading.

        Time: O(n)

        Args:
            path: Path to load the JSON file from

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the JSON data is invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        raw = json.loads(path.read_text())

        # Reset all indexes
        self._contacts = []
        self._bst = ContactBST()
        self._name_trie = Trie()
        self._email_index = {}
        self._recent_heap = []
        self._recent_set = set()

        # Rebuild from data
        for item in raw:
            try:
                contact = Contact.model_validate(item)
                self.add_contact(contact)
            except Exception as e:
                print(f"⚠️  Skipping invalid contact: {e}")

    def get_stats(self) -> dict[str, int]:
        """
        Get store statistics.

        Returns:
            Dictionary with store statistics
        """
        return {
            "total_contacts": len(self._contacts),
            "email_index_size": len(self._email_index),
            "bst_size": len(self._bst),
            "trie_size": len(self._name_trie),
            "recent_heap_size": len(self._recent_heap),
            "max_recent": self.max_recent,
        }

    def find_duplicates(self) -> List[Contact]:
        """
        Find duplicate contacts (by email).

        Returns:
            List of duplicate contacts
        """
        seen: set[str] = set()
        duplicates: List[Contact] = []

        for contact in self._contacts:
            email_key = contact.email.lower()
            if email_key in seen:
                duplicates.append(contact)
            else:
                seen.add(email_key)

        return duplicates

    def __len__(self) -> int:
        """Return number of contacts."""
        return len(self._contacts)

    def __contains__(self, email: str) -> bool:
        """Check if a contact with the given email exists."""
        return email.lower() in self._email_index

    def __repr__(self) -> str:
        """String representation of the store."""
        return f"ContactStore(contacts={len(self)}, emails={len(self._email_index)})"


if __name__ == "__main__":
    print("=== ContactStore Demo ===")

    store = ContactStore(max_recent=5)

    # Add sample contacts
    contacts = [
        Contact(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="(555) 111-2222",
            company="Tech Corp",
        ),
        Contact(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="(555) 333-4444",
            company="Data Inc",
        ),
        Contact(
            first_name="Alice",
            last_name="Brown",
            email="alice.brown@example.com",
            phone="(555) 555-6666",
        ),
        Contact(
            first_name="Bob", last_name="Doe", email="bob.doe@example.com", phone="(555) 777-8888"
        ),
        Contact(
            first_name="Charlie",
            last_name="Johnson",
            email="charlie.j@example.com",
            phone="(555) 999-0000",
        ),
    ]

    for contact in contacts:
        store.add_contact(contact)

    print(f"Store: {store}")
    print(f"\nStatistics: {store.get_stats()}")

    # Test email lookup
    print("\n--- Email Lookup ---")
    found = store.get_by_email("john.doe@example.com")
    print(f"  Found: {found.display() if found else 'None'}")

    # Test alphabetical listing
    print("\n--- Alphabetical Listing ---")
    for i, contact in enumerate(store.get_all_alphabetical(), 1):
        print(f"  {i:2d}. {contact.full_name():<20} {contact.email}")

    # Test autocomplete
    print("\n--- Autocomplete 'do' ---")
    suggestions = store.autocomplete_name("do")
    print(f"  Suggestions: {suggestions}")

    # Test search
    print("\n--- Search 'do' ---")
    results = store.search_by_name("do")
    for contact in results:
        print(f"  {contact.full_name()}")

    # Test recent contacts
    print("\n--- Recent Contacts ---")
    store.contact("alice.brown@example.com")
    store.contact("john.doe@example.com")
    store.contact("jane.smith@example.com")

    for i, contact in enumerate(store.get_recent_contacts(3), 1):
        print(f"  {i}. {contact.full_name()} ({contact.last_contacted.strftime('%H:%M:%S')})")

    # Test save/load
    print("\n--- Save/Load ---")
    save_path = Path("contacts.json")
    store.save(save_path)
    print(f"  Saved {len(store)} contacts to {save_path}")

    new_store = ContactStore()
    new_store.load(save_path)
    print(f"  Loaded {len(new_store)} contacts")

    save_path.unlink()
    print(f"  Removed {save_path}")
