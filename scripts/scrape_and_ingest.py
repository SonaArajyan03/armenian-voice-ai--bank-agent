from __future__ import annotations

import logging
import sys
from pathlib import Path

from bank_support.config import settings
from bank_support.scraping.pipeline import IngestionPipeline


def _validate_openai_key() -> None:
    api_key = settings.openai_api_key.strip()
    if not api_key or api_key == "your_openai_key":
        raise RuntimeError(
            "OPENAI_API_KEY is missing or still set to a placeholder value. "
            "Update .env with a real key before running ingestion."
        )


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    seeds_path = Path("seeds/banks.yaml")
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    if not seeds_path.exists():
        raise RuntimeError(f"Seeds file not found: {seeds_path}")

    _validate_openai_key()
    IngestionPipeline().run(str(seeds_path))
    print("Knowledge base updated.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
