# Photo Metadata Tracker - Day 56 Capstone

What: Stores photo metadata with Pydantic validation, hash map tag index O1, date sorted index O log n insert, Trie autocomplete O m.

How to run:
source.venv/bin/activate
uv pip install -e ".[dev]"
python -m app.photo_tracker

Example:
search beach -> ['IMG_001.jpg', 'IMG_002.png']
autocomplete IMG_0 -> ['IMG_001.jpg', 'IMG_002.png']
