#!/usr/bin/env python3
"""Contact Book CLI v2 — Interactive menu loop"""

import sys
from pathlib import Path

from core.models import Contact
from core.contact_store import ContactStore
from core.csv_handler import export_to_csv, import_from_csv


class ContactCLI:
    def __init__(self) -> None:
        self.store = ContactStore()
        self.csv_dir = Path(__file__).parent.parent / "data"

    def print_menu(self) -> None:
        print("\n" + "=" * 50)
        print("      📇 CONTACT BOOK v2")
        print("=" * 50)
        print("  1. Add Contact")
        print("  2. List All Contacts")
        print("  3. Search by Name")
        print("  4. Search by Tag")
        print("  5. Delete by Email")
        print("  6. Delete ALL Contacts")
        print("  7. Edit Contact")
        print("  8. Export to CSV")
        print("  9. Import from CSV")
        print("  0. Exit")
        print("=" * 50)

    def add_contact(self) -> None:
        print("\n--- Add Contact ---")
        try:
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            tags_input = input("Tags (comma-separated): ").strip()
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            notes = input("Notes (optional): ").strip() or None

            contact = Contact(name=name, email=email, phone=phone, tags=tags, notes=notes)
            self.store.add(contact)
            print(f"✅ Added: {contact.name}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def list_contacts(self) -> None:
        contacts = self.store.list_all()
        if not contacts:
            print("\n📭 No contacts found.")
            return
        print(f"\n--- {len(contacts)} Contact(s) ---")
        for i, c in enumerate(contacts, 1):
            tags_str = ", ".join(c.tags) if c.tags else "none"
            print(f"\n  [{i}] {c.name}")
            print(f"      📧 {c.email}")
            print(f"      📞 {c.phone}")
            print(f"      🏷️  {tags_str}")
            if c.notes:
                print(f"      📝 {c.notes}")

    def search_name(self) -> None:
        query = input("\nSearch name: ").strip()
        results = self.store.find_by_name(query)
        print(f"\n--- {len(results)} Result(s) ---")
        for c in results:
            print(f"  • {c.name} | {c.email} | {c.phone}")

    def search_tag(self) -> None:
        tag = input("\nSearch tag: ").strip()
        results = self.store.find_by_tag(tag)
        print(f"\n--- {len(results)} Result(s) ---")
        for c in results:
            print(f"  • {c.name} | Tags: {', '.join(c.tags)}")

    def delete_contact(self) -> None:
        email = input("\nEmail to delete: ").strip()
        if self.store.delete_by_email(email):
            print("✅ Deleted.")
        else:
            print("❌ Contact not found.")

    def delete_all(self) -> None:
        count = len(self.store.list_all())
        if count == 0:
            print("\n📭 No contacts to delete.")
            return

        print(f"\n⚠️  You are about to delete ALL {count} contact(s).")
        confirm = input("Type 'yes' to confirm: ").strip().lower()
        if confirm == "yes":
            self.store.clear_all()
            print(f"✅ Deleted all {count} contact(s).")
        else:
            print("❌ Cancelled.")

    def edit_contact(self) -> None:
        print("\n--- Edit Contact ---")
        email = input("Email of contact to edit: ").strip()
        contact = self.store.find_by_email(email)

        if not contact:
            print("❌ Contact not found.")
            return

        print(f"\nCurrent: {contact.name} | {contact.email} | {contact.phone}")
        print("Press Enter to keep current value, or type new value.")

        name = input(f"Name [{contact.name}]: ").strip() or contact.name
        new_email = input(f"Email [{contact.email}]: ").strip() or contact.email
        phone = input(f"Phone [{contact.phone}]: ").strip() or contact.phone
        tags_input = input(f"Tags [{', '.join(contact.tags)}]: ").strip()
        tags = (
            [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else contact.tags
        )
        notes_input = input(f"Notes [{contact.notes or 'none'}]: ").strip()
        notes = notes_input if notes_input else contact.notes

        try:
            # Delete old, create new (since email might change)
            self.store.delete_by_email(email)
            updated = Contact(name=name, email=new_email, phone=phone, tags=tags, notes=notes)
            self.store.add(updated)
            print(f"✅ Updated: {updated.name}")
        except Exception as e:
            print(f"❌ Error: {e}")

    def export_csv(self) -> None:
        contacts = self.store.list_all()
        if not contacts:
            print("\n📭 No contacts to export.")
            return

        default_path = self.csv_dir / "contacts_export.csv"
        path_input = input(f"\nExport path [{default_path}]: ").strip()
        filepath = Path(path_input) if path_input else default_path

        try:
            export_to_csv(contacts, filepath)
        except Exception as e:
            print(f"❌ Error: {e}")

    def import_csv(self) -> None:
        default_path = self.csv_dir / "contacts_import.csv"
        path_input = input(f"\nImport path [{default_path}]: ").strip()
        filepath = Path(path_input) if path_input else default_path

        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            print("   Create a CSV with columns: name, email, phone, tags, created_at, notes")
            return

        try:
            imported = import_from_csv(filepath)
            for c in imported:
                # Check for duplicate email
                if self.store.find_by_email(c.email):
                    print(f"⚠️  Skipping duplicate email: {c.email}")
                    continue
                self.store.add(c)
            print(f"✅ Total imported: {len(imported)} contact(s)")
        except Exception as e:
            print(f"❌ Error: {e}")

    def run(self) -> None:
        while True:
            self.print_menu()
            choice = input("Choice: ").strip()

            if choice == "1":
                self.add_contact()
            elif choice == "2":
                self.list_contacts()
            elif choice == "3":
                self.search_name()
            elif choice == "4":
                self.search_tag()
            elif choice == "5":
                self.delete_contact()
            elif choice == "6":
                self.delete_all()
            elif choice == "7":
                self.edit_contact()
            elif choice == "8":
                self.export_csv()
            elif choice == "9":
                self.import_csv()
            elif choice == "0":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice.")


def main() -> None:
    try:
        ContactCLI().run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
