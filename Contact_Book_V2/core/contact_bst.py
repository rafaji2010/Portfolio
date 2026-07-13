"""
core/contact_bst.py
BST for storing contacts by last name
"""

from __future__ import annotations
from typing import Optional, List, Iterator
from core.contact_models import Contact


class BSTNode:
    """Node in a Binary Search Tree."""

    def __init__(self, contact: Contact) -> None:
        self.contact = contact
        self.left: Optional[BSTNode] = None
        self.right: Optional[BSTNode] = None
    
    @property
    def key(self) -> str:
        """Key for BST: last_name, first_name"""
        return f"{self.contact.last_name.lower()},{self.contact.first_name.lower()}"
    
    def __repr__(self) -> str:
        return f"BSTNode({self.contact.full_name()})"


class ContactBST:
    """
    BST storing contacts by last name.
    
    Operations:
    - insert: O(log n) average, O(n) worst
    - search: O(log n) average, O(n) worst
    - inorder_traversal: O(n) for sorted list
    """
    
    def __init__(self) -> None:
        self.root: Optional[BSTNode] = None
        self._size: int = 0
    
    def insert(self, contact: Contact) -> None:
        """Insert a contact into the BST."""
        self.root = self._insert_recursive(self.root, contact)
        self._size += 1
    
    def _insert_recursive(self, node: Optional[BSTNode], contact: Contact) -> BSTNode:
        """Recursive insert helper."""
        if node is None:
            return BSTNode(contact)
        
        # Compare by last name, then first name
        if contact.last_name.lower() < node.contact.last_name.lower():
            node.left = self._insert_recursive(node.left, contact)
        elif contact.last_name.lower() > node.contact.last_name.lower():
            node.right = self._insert_recursive(node.right, contact)
        else:
            # Same last name, compare first name
            if contact.first_name.lower() < node.contact.first_name.lower():
                node.left = self._insert_recursive(node.left, contact)
            elif contact.first_name.lower() > node.contact.first_name.lower():
                node.right = self._insert_recursive(node.right, contact)
            else:
                # Same name - update existing contact
                node.contact = contact
                self._size -= 1  # Don't increment size for update
        
        return node
    
    def search(self, last_name: str, first_name: Optional[str] = None) -> Optional[Contact]:
        """Search for a contact by last name (and optionally first name)."""
        node = self.root
        last_name_lower = last_name.lower()
        first_name_lower = first_name.lower() if first_name else None
        
        while node is not None:
            if last_name_lower < node.contact.last_name.lower():
                node = node.left
            elif last_name_lower > node.contact.last_name.lower():
                node = node.right
            else:
                # Same last name
                if first_name_lower is None:
                    return node.contact
                
                if first_name_lower < node.contact.first_name.lower():
                    node = node.left
                elif first_name_lower > node.contact.first_name.lower():
                    node = node.right
                else:
                    return node.contact
        
        return None
    
    def inorder(self) -> Iterator[Contact]:
        """In-order traversal: returns contacts in alphabetical order."""
        return self._inorder_recursive(self.root)
    
    def _inorder_recursive(self, node: Optional[BSTNode]) -> Iterator[Contact]:
        """Recursive inorder traversal."""
        if node is not None:
            yield from self._inorder_recursive(node.left)
            yield node.contact
            yield from self._inorder_recursive(node.right)
    
    def to_list(self) -> List[Contact]:
        """Return all contacts sorted alphabetically."""
        return list(self.inorder())
    
    def size(self) -> int:
        """Return number of contacts."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if BST is empty."""
        return self.root is None
    
    def __len__(self) -> int:
        return self._size
    
    def __iter__(self) -> Iterator[Contact]:
        return self.inorder()


if __name__ == "__main__":
    print("=== Contact BST Demo ===")
    
    bst = ContactBST()
    
    # Add sample contacts
    contacts = [
        Contact(
            first_name="John", last_name="Doe",
            email="john@example.com", phone="555-111-2222"
        ),
        Contact(
            first_name="Jane", last_name="Smith",
            email="jane@example.com", phone="555-333-4444"
        ),
        Contact(
            first_name="Alice", last_name="Brown",
            email="alice@example.com", phone="555-555-6666"
        ),
        Contact(
            first_name="Bob", last_name="Doe",
            email="bob@example.com", phone="555-777-8888"
        )
    ]
    
    for contact in contacts:
        bst.insert(contact)
    
    print(f"BST size: {bst.size()}")
    print("\nContacts in alphabetical order:")
    for i, contact in enumerate(bst.inorder(), 1):
        print(f"  {i}. {contact.full_name()} ({contact.email})")
    
    print("\nSearch for 'Doe':")
    result = bst.search("Doe")
    print(f"  Found: {result.full_name() if result else 'None'}")
    
    print("\nSearch for 'Doe, John':")
    result = bst.search("Doe", "John")
    print(f"  Found: {result.full_name() if result else 'None'}")