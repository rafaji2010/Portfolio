"""Core data structures and contact storage for Contact Book v2."""

__all__ = ["Contact", "ContactStore"]


def __getattr__(name: str) -> object:
    """Lazy imports to avoid circular import warnings when running modules directly."""
    if name == "Contact":
        from core.contact_models import Contact

        return Contact
    if name == "ContactStore":
        from core.contact_store import ContactStore

        return ContactStore
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
