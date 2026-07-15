"""CSV import/export for Contact Book"""

import csv
from pathlib import Path
from typing import List, Sequence, Any, Dict
from core.models import Contact


def export_to_csv(contacts: List[Contact], filepath: Path) -> None:
    """Export contacts to our standard CSV format."""
    if not contacts:
        raise ValueError("No contacts to export")

    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email", "phone", "tags", "created_at", "notes"])
        for c in contacts:
            writer.writerow(
                [
                    c.name,
                    c.email,
                    c.phone,
                    "|".join(c.tags),
                    c.created_at.isoformat(),
                    c.notes or "",
                ]
            )

    print(f"✅ Exported {len(contacts)} contact(s) to {filepath}")


def _is_google_contacts_format(fieldnames: Sequence[str]) -> bool:
    """Detect Google Contacts export format."""
    if not fieldnames:
        return False
    google_indicators = ["Given Name", "Family Name", "Phone [Value]", "E-mail [Value]"]
    return any(ind in fieldnames for ind in google_indicators)


def _parse_google_contacts_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Google Contacts row to our format."""
    # Name: combine Given + Family, or use full Name
    name = row.get("Name", "").strip()
    if not name:
        given = row.get("Given Name", "").strip()
        family = row.get("Family Name", "").strip()
        name = f"{given} {family}".strip()

    # Email: E-mail [Value] may have multiple emails separated by :::
    email_raw = row.get("E-mail [Value]", "").strip()
    email = email_raw.split(":::")[0].strip() if email_raw else ""

    # Phone: Phone [Value] may have multiple phones separated by :::
    phone_raw = row.get("Phone [Value]", "").strip()
    phone = phone_raw.split(":::")[0].strip() if phone_raw else ""

    # Tags: use Organization as a tag, or empty
    tags = []
    org = row.get("Organization [Value]", "").strip()
    if org:
        tags.append(org)
    title = row.get("Organization [Title]", "").strip()
    if title:
        tags.append(title)

    # Notes
    notes = row.get("Notes", "").strip() or None

    return {"name": name, "email": email, "phone": phone, "tags": tags, "notes": notes}


def import_from_csv(filepath: Path) -> List[Contact]:
    """Import contacts from CSV. Auto-detects Google Contacts or our format."""
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    contacts = []
    errors = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        is_google = _is_google_contacts_format(fieldnames)

        if is_google:
            print("📇 Detected Google Contacts format. Converting...")
        else:
            print("📇 Using standard format.")

        for row_num, row in enumerate(reader, start=2):
            try:
                if is_google:
                    parsed = _parse_google_contacts_row(row)
                else:
                    # Standard format
                    tags_raw = row.get("tags", "")
                    tags = [t.strip() for t in tags_raw.replace(",", "|").split("|") if t.strip()]
                    parsed = {
                        "name": row.get("name", "").strip(),
                        "email": row.get("email", "").strip(),
                        "phone": row.get("phone", "").strip(),
                        "tags": tags,
                        "notes": row.get("notes", "").strip() or None,
                    }

                # Skip empty rows
                if not parsed["name"] and not parsed["email"]:
                    continue

                contact = Contact(
                    name=parsed["name"],
                    email=parsed["email"],
                    phone=parsed["phone"],
                    tags=parsed["tags"],
                    notes=parsed["notes"],
                )
                contacts.append(contact)
            except Exception as e:
                errors.append(f"Row {row_num}: {e}")

    if errors:
        print(f"⚠️  {len(errors)} row(s) skipped:")
        for err in errors:
            print(f"   • {err}")

    print(f"✅ Imported {len(contacts)} contact(s) from {filepath}")
    return contacts
