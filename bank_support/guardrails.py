from __future__ import annotations

import re
from dataclasses import dataclass

ALLOWED_TOPICS = {
    "credits": [
        "credit",
        "loan",
        "mortgage",
        "վարկ",
        "հիփոթեք",
        "overdraft",
    ],
    "deposits": ["deposit", "term deposit", "savings", "ավանդ", "խնայող"],
    "branch_locations": [
        "branch",
        "atm",
        "location",
        "address",
        "hours",
        "մասնաճյուղ",
        "բանկոմատ",
        "հասցե",
        "աշխատանքային ժամ",
    ],
}

BLOCKED_HINTS = [
    "card",
    "swift",
    "exchange rate",
    "transfer",
    "insurance",
    "crypto",
    "investment",
    "account opening",
    "fees",
    "tariff",
    "debit",
    "credit card",
    "քարտ",
    "փոխանց",
    "փոխարժեք",
    "ապահովագր",
]

BANK_ALIASES = {
    "mellat bank": ["mellat", "mellat bank", "մելլաթ"],
    "ameriabank": ["ameriabank", "ameria", "ամերիա", "ամերիաբանկ"],
    "acba": ["acba", "ակբա"],
}


@dataclass(slots=True)
class ScopeResult:
    in_scope: bool
    topic: str | None
    banks: list[str]
    language: str
    reason: str



def _contains_any(text: str, variants: list[str]) -> bool:
    return any(item in text for item in variants)



def detect_scope(user_text: str) -> ScopeResult:
    normalized = re.sub(r"\s+", " ", user_text.lower()).strip()
    language = "hy" if re.search(r"[\u0530-\u058F]", normalized) else "en"

    topic = None
    for candidate, keywords in ALLOWED_TOPICS.items():
        if _contains_any(normalized, keywords):
            topic = candidate
            break

    blocked = _contains_any(normalized, BLOCKED_HINTS)
    banks = [name for name, aliases in BANK_ALIASES.items() if _contains_any(normalized, aliases)]

    if blocked and topic is None:
        return ScopeResult(False, None, banks, language, "unsupported_topic")
    if topic is None:
        return ScopeResult(False, None, banks, language, "no_supported_topic_detected")

    return ScopeResult(True, topic, banks, language, "ok")


REFUSALS = {
    "hy": {
        "unsupported": "Ներեցեք, ես կարող եմ պատասխանել միայն վարկերի, ավանդների և մասնաճյուղերի հասցեների վերաբերյալ հարցերի։",
        "missing": "Ներեցեք, այս հարցին պատասխանելու համար բավարար հաստատված տվյալ չունեմ բանկի կայքի ներբեռնված նյութերում։",
    },
    "en": {
        "unsupported": "Sorry, I can only help with credits, deposits, and branch locations.",
        "missing": "Sorry, I do not have enough verified information in the ingested bank website data to answer that.",
    },
}
