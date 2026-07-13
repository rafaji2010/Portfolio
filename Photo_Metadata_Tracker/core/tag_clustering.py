from __future__ import annotations
from core.models import Photo
from core.union_find import UnionFind

def cluster_tags(photos: list[Photo]) -> dict[str, list[str]]:
    uf = UnionFind()
    for p in photos:
        if len(p.tags) < 2:
            continue
        first = p.tags[0]
        for t in p.tags[1:]:
            uf.union(first, t)

    clusters: dict[str, list[str]] = {}
    for p in photos:
        for tag in p.tags:
            root = uf.find(tag)
            if root not in clusters:
                clusters[root] = []
            if tag not in clusters[root]:
                clusters[root].append(tag)
    return clusters
