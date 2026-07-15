# core/photo_store.py
from __future__ import annotations
from datetime import datetime
import json
from pathlib import Path
from bisect import insort
from core.models import Photo
from core.trie import Trie


class PhotoStore:
    def __init__(self) -> None:
        self.photos: list[Photo] = []
        self.tag_index: dict[str, list[int]] = {}  # tag -> list of indices in photos
        self.date_index: list[tuple[datetime, int]] = (
            []
        )  # sorted by date, stores (date, idx)
        self.filename_trie: Trie = Trie()

    def add_photo(self, photo: Photo) -> int:
        idx = len(self.photos)
        self.photos.append(photo)

        # 1. Tag hash map O1 average insert
        for tag in photo.tags:
            self.tag_index.setdefault(tag, []).append(idx)

        # 2. Date sorted index O log n insert via bisect
        insort(self.date_index, (photo.date_taken, idx))

        # 3. Filename trie O m where m is filename length
        self.filename_trie.insert(photo.filename)
        return idx

    def search_by_tag(self, tag: str) -> list[Photo]:
        key = tag.strip().lower()
        indices = self.tag_index.get(key, [])
        return [self.photos[i] for i in indices]

    def sort_by_date(self, reverse: bool = False) -> list[Photo]:
        ordered = reversed(self.date_index) if reverse else self.date_index
        return [self.photos[i] for _, i in ordered]

    def autocomplete_filename(self, prefix: str) -> list[str]:
        return self.filename_trie.starts_with(prefix)

    def save(self, path: Path) -> None:
        data = [p.model_dump(mode="json") for p in self.photos]
        path.write_text(json.dumps(data, indent=2))

    def load(self, path: Path) -> None:
        raw = json.loads(path.read_text())
        self.photos = []
        self.tag_index.clear()
        self.date_index.clear()
        self.filename_trie = Trie()
        for item in raw:
            self.add_photo(Photo.model_validate(item))
