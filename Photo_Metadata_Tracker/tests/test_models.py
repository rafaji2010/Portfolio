import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from core.models import Photo


def test_valid_photo():
    photo = Photo(
        filename="vacation.jpg",
        size_kb=1500.5,
        date_taken=datetime(2026, 5, 1, 12, 0),
        tags=["travel", "beach"],
        resolution_mp=24.0,
    )
    assert photo.filename == "vacation.jpg"
    assert photo.size_kb == 1500.5
    assert photo.date_taken == datetime(2026, 5, 1, 12, 0)
    assert photo.tags == ["travel", "beach"]
    assert photo.resolution_mp == 24.0


def test_invalid_extension():
    with pytest.raises(ValidationError):
        Photo(
            filename="document.pdf",
            size_kb=1500.5,
            date_taken=datetime(2026, 5, 1, 12, 0),
            tags=["doc"],
        )


def test_invalid_size():
    with pytest.raises(ValidationError):
        Photo(
            filename="image.png",
            size_kb=-10.0,
            date_taken=datetime(2026, 5, 1, 12, 0),
            tags=["tag"],
        )


def test_future_date():
    future_time = datetime.now() + timedelta(days=2)
    with pytest.raises(ValidationError):
        Photo(
            filename="future.webp",
            size_kb=2000.0,
            date_taken=future_time,
            tags=["future"],
        )


def test_empty_tags():
    with pytest.raises(ValidationError):
        Photo(filename="no_tags.jpg", size_kb=100.0, date_taken=datetime.now(), tags=[])
