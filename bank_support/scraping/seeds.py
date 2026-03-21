from __future__ import annotations

import yaml

from bank_support.scraping.base import SeedPage


def load_seed_pages(path: str) -> list[SeedPage]:
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    pages: list[SeedPage] = []
    for item in raw["pages"]:
        pages.append(SeedPage(**item))
    return pages
