from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank TEXT NOT NULL,
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    language TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    embedding_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    title,
    content,
    bank UNINDEXED,
    topic UNINDEXED,
    url UNINDEXED,
    language UNINDEXED,
    content='documents',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
  INSERT INTO documents_fts(rowid, title, content, bank, topic, url, language)
  VALUES (new.id, new.title, new.content, new.bank, new.topic, new.url, new.language);
END;

CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
  INSERT INTO documents_fts(documents_fts, rowid, title, content, bank, topic, url, language)
  VALUES('delete', old.id, old.title, old.content, old.bank, old.topic, old.url, old.language);
END;

CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
  INSERT INTO documents_fts(documents_fts, rowid, title, content, bank, topic, url, language)
  VALUES('delete', old.id, old.title, old.content, old.bank, old.topic, old.url, old.language);
  INSERT INTO documents_fts(rowid, title, content, bank, topic, url, language)
  VALUES (new.id, new.title, new.content, new.bank, new.topic, new.url, new.language);
END;
"""


class KnowledgeStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert_documents(self, rows: Iterable[dict]) -> None:
        with self.conn:
            for row in rows:
                self.conn.execute(
                    """
                    INSERT INTO documents(bank, topic, title, url, language, content, metadata_json, embedding_json)
                    VALUES(:bank, :topic, :title, :url, :language, :content, :metadata_json, :embedding_json)
                    ON CONFLICT(url) DO UPDATE SET
                      bank=excluded.bank,
                      topic=excluded.topic,
                      title=excluded.title,
                      language=excluded.language,
                      content=excluded.content,
                      metadata_json=excluded.metadata_json,
                      embedding_json=excluded.embedding_json
                    """,
                    {
                        **row,
                        "metadata_json": json.dumps(row.get("metadata", {}), ensure_ascii=False),
                        "embedding_json": json.dumps(row.get("embedding")) if row.get("embedding") else None,
                    },
                )

    def fetch_all(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM documents").fetchall()
