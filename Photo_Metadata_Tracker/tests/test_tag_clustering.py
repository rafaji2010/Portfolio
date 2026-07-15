import pytest
from datetime import datetime
from core.models import Photo
from core.tag_clustering import cluster_tags


def test_tag_clustering():
    p1 = Photo(
        filename="img1.jpg",
        size_kb=100.0,
        date_taken=datetime.now(),
        tags=["sunset", "beach"],
    )
    p2 = Photo(
        filename="img2.jpg",
        size_kb=100.0,
        date_taken=datetime.now(),
        tags=["beach", "ocean"],
    )
    p3 = Photo(
        filename="img3.jpg",
        size_kb=100.0,
        date_taken=datetime.now(),
        tags=["portrait", "studio"],
    )
    p4 = Photo(
        filename="img4.jpg", size_kb=100.0, date_taken=datetime.now(), tags=["macro"]
    )

    clusters = cluster_tags([p1, p2, p3, p4])

    groups = list(clusters.values())
    sorted_groups = sorted([sorted(g) for g in groups], key=len, reverse=True)

    assert len(sorted_groups) >= 2
    assert sorted_groups[0] == ["beach", "ocean", "sunset"]
    assert sorted_groups[1] == ["portrait", "studio"]
