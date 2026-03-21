from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RetrievedChunk:
    bank: str
    topic: str
    url: str
    title: str
    content: str
    language: str
    metadata: dict[str, Any]
    lexical_score: float
    vector_score: float
    final_score: float
