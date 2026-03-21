from __future__ import annotations

import logging
from pathlib import Path

from openai import OpenAI

from bank_support.config import settings
from bank_support.database import KnowledgeStore
from bank_support.scraping.base import Scraper
from bank_support.scraping.seeds import load_seed_pages

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self):
        Path(settings.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        self.store = KnowledgeStore(settings.sqlite_path)
        self.scraper = Scraper(settings.scraper_user_agent)
        self.client = OpenAI(api_key=settings.openai_api_key)

    def embed(self, text: str) -> list[float]:
        resp = self.client.embeddings.create(model=settings.embedding_model, input=text)
        return resp.data[0].embedding

    def run(self, seeds_path: str) -> None:
        seeds_file = Path(seeds_path)
        if not seeds_file.exists():
            raise RuntimeError(f"Seeds file not found: {seeds_file}")

        rows = []
        failures = 0
        for seed in load_seed_pages(str(seeds_file)):
            try:
                doc = self.scraper.fetch(seed)
                try:
                    doc["embedding"] = self.embed(doc["title"] + "\n\n" + doc["content"][:6000])
                except Exception as exc:
                    logger.warning(
                        "Embedding failed for %s (%s, %s): %s. Continuing without embedding.",
                        seed.url,
                        seed.bank,
                        seed.topic,
                        exc,
                    )
                    doc["embedding"] = None
                rows.append(doc)
            except Exception as exc:
                failures += 1
                logger.warning(
                    "Failed to ingest %s (%s, %s): %s",
                    seed.url,
                    seed.bank,
                    seed.topic,
                    exc,
                )

        if not rows:
            raise RuntimeError(
                f"No documents were ingested from {seeds_file}. "
                f"Failed pages: {failures}."
            )

        self.store.upsert_documents(rows)
        logger.info("Knowledge base updated with %s documents (%s failed).", len(rows), failures)
