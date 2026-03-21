from __future__ import annotations

import json
from typing import Iterable

from openai import OpenAI

from bank_support.config import settings
from bank_support.guardrails import REFUSALS, detect_scope
from bank_support.models import RetrievedChunk
from bank_support.prompts import ANSWER_PROMPT_TEMPLATE
from bank_support.retrieval import HybridRetriever


class BankSupportOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        try:
            self.retriever = HybridRetriever(settings.sqlite_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize retriever: {exc}") from exc

    @staticmethod
    def _format_evidence(chunks: Iterable[RetrievedChunk]) -> str:
        payload = []
        for chunk in chunks:
            payload.append(
                {
                    "bank": chunk.bank,
                    "topic": chunk.topic,
                    "title": chunk.title,
                    "url": chunk.url,
                    "content": chunk.content[:2500],
                    "metadata": chunk.metadata,
                }
            )
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def answer(self, question: str) -> str:
        scope = detect_scope(question)
        lang = scope.language
        if not scope.in_scope or not scope.topic:
            return REFUSALS[lang]["unsupported"]

        chunks = self.retriever.search(question=question, topic=scope.topic, banks=scope.banks)
        if not chunks:
            return REFUSALS[lang]["missing"]

        response = self.client.responses.create(
            model=settings.llm_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict banking QA agent. Only answer from the supplied evidence. "
                        "If evidence is insufficient, answer exactly with INSUFFICIENT_EVIDENCE. "
                        "Respond in Armenian unless the user asked in English."
                    ),
                },
                {
                    "role": "user",
                    "content": ANSWER_PROMPT_TEMPLATE.format(
                        question=question,
                        evidence=self._format_evidence(chunks),
                    ),
                },
            ],
            temperature=0.1,
        )
        text = response.output_text.strip()
        if "INSUFFICIENT_EVIDENCE" in text.upper():
            return REFUSALS[lang]["missing"]
        return text
