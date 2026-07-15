# core/models.py
from __future__ import annotations
from datetime import datetime, date
from pathlib import Path
from pydantic import BaseModel, field_validator

ALLOWED_EXTENSIONS: set[str] = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".raw",
    ".heic",
    ".tiff",
}


class Photo(BaseModel):
    filename: str
    size_kb: float
    date_taken: datetime
    tags: list[str]
    resolution_mp: float = 12.0

    @field_validator("filename")
    @classmethod
    def validate_extension(cls, v: str) -> str:
        ext = Path(v).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"filename must end with one of {sorted(ALLOWED_EXTENSIONS)}, got {ext}"
            )
        return v

    @field_validator("size_kb")
    @classmethod
    def validate_size(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("size_kb must be greater than 0")
        return v

    @field_validator("date_taken")
    @classmethod
    def validate_date(cls, v: datetime) -> datetime:
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.now()
        if v.date() > now.date():
            raise ValueError("date_taken cannot be in the future")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("at least one tag required")
        cleaned = [t.strip().lower() for t in v if t.strip()]
        if not cleaned:
            raise ValueError("tags cannot be empty strings")
        return cleaned
