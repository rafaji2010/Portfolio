# app/photo_tracker.py
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from core.models import Photo
from core.photo_store import PhotoStore

def demo() -> None:
    store = PhotoStore()
    p1 = Photo(filename="IMG_001.jpg", size_kb=3200.5, date_taken=datetime(2026,5,1,18,30), tags=["beach","sunset"], resolution_mp=24.0)
    p2 = Photo(filename="IMG_002.png", size_kb=1800.0, date_taken=datetime(2026,5,3,9,15), tags=["beach","portrait"], resolution_mp=12.0)
    store.add_photo(p1)
    store.add_photo(p2)

    print("search beach:", [p.filename for p in store.search_by_tag("beach")])
    print("sorted:", [p.filename for p in store.sort_by_date()])
    print("autocomplete IMG_0:", store.autocomplete_filename("IMG_0"))

    store.save(Path("photos.json"))

if __name__ == "__main__":
    demo()