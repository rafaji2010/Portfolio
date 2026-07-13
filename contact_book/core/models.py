from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class Contact(BaseModel):
    name: str
    email: EmailStr
    phone: str
    tags: list[str] = []
    created_at: datetime = datetime.now()
    notes: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = ''.join(c for c in v if c.isdigit())
        if len(cleaned) < 7:
            raise ValueError('Phone must have at least 7 digits')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
