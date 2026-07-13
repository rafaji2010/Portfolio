"""
app/contact_book.py
CLI interface for Contact Book v2
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from core.contact_models import Contact
from core.contact_store import ContactStore


class ContactBookCLI:
    """CLI interface for Contact Book."""
    
    def __init__(self, data_file: Optional[Path] = None):
        self.store = ContactStore(max_recent=10)
        self.data_file = data_file or Path("contacts.json")
        
        # Load existing data if available
        if self.data_file.exists():
            try:
                self.store.load(self.data_file)
                print(f"✅ Loaded {len(self.store)} contacts from {self.data_file}")
            except Exception as e:
                print(f"⚠️  Could not load data: {e}")
    
    def run(self) -> None:
        """Main CLI loop."""
        print("\n📇 Contact Book v2")
        print("=" * 40)
        print("A multi-index contact management system")
        print(f"Data file: {self.data_file}")
        
        while True:
            print("\nCommands:")
            print("  ┌─────────────────────────────────────────────┐")
            print("  │  add      - Add a new contact               │")
            print("  │  search   - Search by name (prefix)         │")
            print("  │  lookup   - Look up by email                │")
            print("  │  list     - List all contacts (alphabetical)│")
            print("  │  recent   - Show recent contacts            │")
            print("  │  contact  - Record a contact interaction    │")
            print("  │  save     - Save to JSON                   │")
            print("  │  stats    - Show store statistics          │")
            print("  │  quit     - Exit                          │")
            print("  └─────────────────────────────────────────────┘")
            
            choice = input("\n> ").strip().lower()
            
            if choice == "add":
                self._add_contact()
            elif choice == "search":
                self._search_contacts()
            elif choice == "lookup":
                self._lookup_email()
            elif choice == "list":
                self._list_contacts()
            elif choice == "recent":
                self._show_recent()
            elif choice == "contact":
                self._record_contact()
            elif choice == "save":
                self._save_data()
            elif choice == "stats":
                self._show_stats()
            elif choice in ["quit", "q", "exit"]:
                self._save_data()
                print("👋 Goodbye!")
                break
            else:
                print(f"❌ Unknown command: {choice}")
    
    def _add_contact(self) -> None:
        """Add a new contact with validation."""
        print("\n--- Add Contact ---")
        print("Press Enter to skip optional fields")
        print("=" * 40)
        
        first_name = input("First Name: ").strip()
        if not first_name:
            print("❌ First name is required")
            return
        
        last_name = input("Last Name: ").strip()
        if not last_name:
            print("❌ Last name is required")
            return
        
        email = input("Email: ").strip()
        if not email:
            print("❌ Email is required")
            return
        
        # Check for duplicate
        existing = self.store.get_by_email(email)
        if existing:
            print(f"⚠️  Contact with email {email} already exists:")
            print(f"   {existing.full_name()} - {existing.phone}")
            choice = input("  Update existing? (y/n): ").strip().lower()
            if choice != 'y':
                return
        
        phone = input("Phone: ").strip()
        if not phone:
            print("❌ Phone is required")
            return
        
        company = input("Company (optional): ").strip()
        notes = input("Notes (optional): ").strip()
        
        try:
            contact = Contact(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company if company else None,
                notes=notes if notes else None
            )
            
            idx = self.store.add_contact(contact)
            print(f"✅ Contact added successfully!")
            print(f"   Index: {idx}")
            print(f"   Name: {contact.full_name()}")
            print(f"   Email: {contact.email}")
            
        except ValueError as e:
            print(f"❌ Validation error: {e}")
    
    def _search_contacts(self) -> None:
        """Search contacts by name prefix."""
        print("\n--- Search Contacts ---")
        print("=" * 40)
        query = input("Name prefix: ").strip()
        
        if not query:
            print("❌ Query is required")
            return
        
        # Show autocomplete suggestions first
        suggestions = self.store.autocomplete_name(query)
        if suggestions:
            print(f"\n💡 Suggestions: {', '.join(suggestions[:5])}")
            if len(suggestions) > 5:
                print(f"   ... and {len(suggestions) - 5} more")
        
        results = self.store.search_by_name(query)
        
        if results:
            print(f"\n✅ Found {len(results)} contacts:")
            print("-" * 40)
            for i, contact in enumerate(results, 1):
                print(f"  {i}. {contact.full_name()}")
                print(f"     📧 {contact.email}")
                print(f"     📞 {contact.phone}")
                if contact.company:
                    print(f"     🏢 {contact.company}")
                if contact.last_contacted:
                    print(f"     📅 {contact.last_contacted.strftime('%Y-%m-%d')}")
                print()
        else:
            print(f"❌ No contacts matching '{query}'")
    
    def _lookup_email(self) -> None:
        """Look up contact by email."""
        print("\n--- Email Lookup ---")
        print("=" * 40)
        email = input("Email: ").strip()
        
        if not email:
            print("❌ Email is required")
            return
        
        contact = self.store.get_by_email(email)
        
        if contact:
            print(f"\n✅ Contact found:")
            print("=" * 40)
            print(f"  Name: {contact.full_name()}")
            print(f"  Email: {contact.email}")
            print(f"  Phone: {contact.phone}")
            if contact.company:
                print(f"  Company: {contact.company}")
            if contact.notes:
                print(f"  Notes: {contact.notes}")
            print(f"  Last Contacted: {contact.last_contacted.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"❌ No contact found with email '{email}'")
    
    def _list_contacts(self) -> None:
        """List all contacts alphabetically."""
        print("\n--- All Contacts (Alphabetical) ---")
        print("=" * 40)
        contacts = self.store.get_all_alphabetical()
        
        if contacts:
            print(f"📇 Total: {len(contacts)} contacts")
            print("-" * 40)
            for i, contact in enumerate(contacts, 1):
                print(f"  {i:2d}. {contact.full_name():<20} {contact.email:<30} {contact.phone}")
        else:
            print("❌ No contacts in store")
    
    def _show_recent(self) -> None:
        """Show recently contacted contacts."""
        print("\n--- Recent Contacts ---")
        print("=" * 40)
        n_input = input("Number to show (default 5): ").strip()
        n = int(n_input) if n_input else 5
        
        contacts = self.store.get_recent_contacts(n)
        
        if contacts:
            print(f"🕐 Most recent {len(contacts)} contacts:")
            print("-" * 40)
            for i, contact in enumerate(contacts, 1):
                time_str = contact.last_contacted.strftime("%Y-%m-%d %H:%M")
                print(f"  {i}. {contact.full_name()}")
                print(f"     📧 {contact.email}")
                print(f"     🕐 {time_str}")
                print()
        else:
            print("❌ No recent contacts")
    
    def _record_contact(self) -> None:
        """Record a contact interaction."""
        print("\n--- Record Contact ---")
        print("=" * 40)
        email = input("Contact email: ").strip()
        
        if not email:
            print("❌ Email is required")
            return
        
        contact = self.store.contact(email)
        
        if contact:
            print(f"✅ Recorded contact with {contact.full_name()}")
            print(f"   Email: {contact.email}")
            print(f"   Last contacted: {contact.last_contacted.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"❌ No contact found with email '{email}'")
    
    def _show_stats(self) -> None:
        """Show store statistics."""
        print("\n--- Store Statistics ---")
        print("=" * 40)

        stats = self.store.get_stats()
        total = stats["total_contacts"]

        print("📊 Contact Store Statistics:")
        print(f"  Total contacts: {total}")
        print(f"  Email index size: {stats['email_index_size']}")
        print(f"  BST size: {stats['bst_size']}")
        print(f"  Trie size: {stats['trie_size']}")
        print(f"  Recent contacts tracked: {stats['recent_heap_size']}")
        
        if total > 0:
            # Show first 5 contacts as preview
            print("\n📋 Contact Preview (first 5):")
            print("-" * 40)
            for i, contact in enumerate(self.store.get_all_alphabetical()[:5], 1):
                print(f"  {i}. {contact.full_name()} <{contact.email}>")
            if total > 5:
                print(f"  ... and {total - 5} more")
    
    def _save_data(self) -> None:
        """Save data to JSON."""
        print("\n--- Saving Data ---")
        print("=" * 40)
        try:
            self.store.save(self.data_file)
            print(f"✅ Saved {len(self.store)} contacts to {self.data_file}")
        except Exception as e:
            print(f"❌ Failed to save: {e}")


def demo() -> None:
    """Quick demo without CLI."""
    print("\n📸 Contact Book V2 Demo")
    print("=" * 50)
    
    store = ContactStore()
    
    # Add sample contacts
    sample_contacts = [
        Contact(
            first_name="John", last_name="Doe",
            email="john.doe@example.com", phone="(555) 111-2222",
            company="Tech Corp"
        ),
        Contact(
            first_name="Jane", last_name="Smith",
            email="jane.smith@example.com", phone="(555) 333-4444",
            company="Data Inc"
        ),
        Contact(
            first_name="Alice", last_name="Brown",
            email="alice.brown@example.com", phone="(555) 555-6666"
        ),
        Contact(
            first_name="Bob", last_name="Doe",
            email="bob.doe@example.com", phone="(555) 777-8888",
            company="Tech Corp"
        ),
        Contact(
            first_name="Charlie", last_name="Johnson",
            email="charlie.johnson@example.com", phone="(555) 999-0000",
            notes="Met at conference"
        )
    ]
    
    print("Adding sample contacts...")
    for contact in sample_contacts:
        idx = store.add_contact(contact)
        print(f"  ✅ Added: {contact.full_name()} (index {idx})")
    
    print(f"\n📊 Store: {store}")
    
    print("\n--- All Contacts (Alphabetical) ---")
    for i, contact in enumerate(store.get_all_alphabetical(), 1):
        print(f"  {i:2d}. {contact.full_name():<20} {contact.email}")
    
    print("\n--- Autocomplete 'do' ---")
    suggestions = store.autocomplete_name("do")
    print(f"  Suggestions: {suggestions}")
    
    print("\n--- Email Lookup 'john.doe@example.com' ---")
    found = store.get_by_email("john.doe@example.com")
    if found:
        print(f"  ✅ Found: {found.full_name()}")
        print(f"     Phone: {found.phone}")
        print(f"     Company: {found.company}")
    
    print("\n--- Recent Contacts ---")
    # Simulate some contacts
    store.contact("alice.brown@example.com")
    store.contact("john.doe@example.com")
    store.contact("jane.smith@example.com")
    
    for i, contact in enumerate(store.get_recent_contacts(3), 1):
        print(f"  {i}. {contact.full_name()} (last: {contact.last_contacted.strftime('%H:%M:%S')})")
    
    # Save demo data
    save_path = Path("demo_contacts.json")
    store.save(save_path)
    print(f"\n💾 Saved {len(store)} contacts to {save_path}")
    
    # Load demo data
    new_store = ContactStore()
    new_store.load(save_path)
    print(f"📂 Loaded {len(new_store)} contacts from {save_path}")
    
    # Clean up
    save_path.unlink()
    print(f"🗑️  Removed {save_path}")
    
    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        cli = ContactBookCLI()
        cli.run()