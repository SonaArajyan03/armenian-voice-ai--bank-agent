from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from typing import Iterable

from openai import OpenAI

from bank_support.config import settings
from bank_support.models import RetrievedChunk


class HybridRetriever:
    def __init__(self, db_path: str | Path):
        resolved_path = Path(db_path)
        if not resolved_path.exists():
            raise RuntimeError(
                f"Knowledge DB not found at {resolved_path}. "
                "Run: python scripts/scrape_and_ingest.py"
            )

        self.conn = sqlite3.connect(resolved_path)
        self.conn.row_factory = sqlite3.Row
        self.client = OpenAI(api_key=settings.openai_api_key)

    def _embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=settings.embedding_model, input=text)
        return response.data[0].embedding

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        if not na or not nb:
            return 0.0
        return dot / (na * nb)

    def search(self, question: str, topic: str, banks: Iterable[str] | None = None) -> list[RetrievedChunk]:
        filters = ["topic = ?"]
        params: list[str] = [topic]
        bank_list = list(banks or [])
        if bank_list:
            filters.append("bank IN (%s)" % ",".join("?" for _ in bank_list))
            params.extend(bank_list)

        lexical_rows = self.conn.execute(
            f"""
            SELECT d.*, bm25(documents_fts) AS lexical_score
            FROM documents_fts
            JOIN documents d ON d.id = documents_fts.rowid
            WHERE documents_fts MATCH ? AND {' AND '.join(filters)}
            ORDER BY lexical_score
            LIMIT ?
            """,
            [question, *params, settings.search_top_k * 3],
        ).fetchall()

        query_embedding = self._embed(question)
        ranked: list[RetrievedChunk] = []
        for row in lexical_rows:
            embedding = json.loads(row["embedding_json"]) if row["embedding_json"] else None
            vector_score = self._cosine(query_embedding, embedding) if embedding else 0.0
            lexical_score = 1 / (1 + abs(float(row["lexical_score"])))
            final_score = (0.55 * lexical_score) + (0.45 * vector_score)
            ranked.append(
                RetrievedChunk(
                    bank=row["bank"],
                    topic=row["topic"],
                    url=row["url"],
                    title=row["title"],
                    content=row["content"],
                    language=row["language"],
                    metadata=json.loads(row["metadata_json"]),
                    lexical_score=lexical_score,
                    vector_score=vector_score,
                    final_score=final_score,
                )
            )

        ranked.sort(key=lambda x: x.final_score, reverse=True)
        return [r for r in ranked if r.final_score >= settings.min_retrieval_score][: settings.max_context_chunks]
