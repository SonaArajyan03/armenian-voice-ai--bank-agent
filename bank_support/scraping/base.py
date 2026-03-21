from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md


@dataclass(slots=True)
class SeedPage:
    bank: str
    topic: str
    url: str
    language: str = "hy"


class Scraper:
    def __init__(self, user_agent: str):
        self.client = httpx.Client(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": user_agent},
        )

    def fetch(self, seed: SeedPage) -> dict[str, Any]:
        response = self.client.get(seed.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else seed.url

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        main = soup.find("main") or soup.body or soup
        text = md(str(main), heading_style="ATX")
        clean_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        return {
            "bank": seed.bank,
            "topic": seed.topic,
            "title": title,
            "url": seed.url,
            "language": seed.language,
            "content": clean_text[:12000],
            "metadata": {},
        }
