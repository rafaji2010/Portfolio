import pytest
from datetime import datetime
from pathlib import Path
from core.models import Photo
from core.photo_store import PhotoStore


@pytest.fixture
def store():
    return PhotoStore()


def test_store_operations(store, tmp_path):
    p1 = Photo(
        filename="IMG_001.jpg",
        size_kb=3200.5,
        date_taken=datetime(2026, 5, 1, 18, 30),
        tags=["beach", "sunset"],
    )
    p2 = Photo(
        filename="IMG_002.png",
        size_kb=1800.0,
        date_taken=datetime(2026, 5, 3, 9, 15),
        tags=["beach", "portrait"],
    )

    store.add_photo(p1)
    store.add_photo(p2)

    results = store.search_by_tag("beach")
    assert len(results) == 2
    assert {p.filename for p in results} == {"IMG_001.jpg", "IMG_002.png"}

    sorted_photos = store.sort_by_date()
    assert [p.filename for p in sorted_photos] == ["IMG_001.jpg", "IMG_002.png"]

    suggestions = store.autocomplete_filename("IMG_0")
    assert "IMG_001.jpg" in suggestions
    assert "IMG_002.png" in suggestions

    # Test persistence
    save_file = tmp_path / "photos_test.json"
    store.save(save_file)

    new_store = PhotoStore()
    new_store.load(save_file)
    assert len(new_store.photos) == 2
    assert new_store.photos[0].filename == "IMG_001.jpg"
