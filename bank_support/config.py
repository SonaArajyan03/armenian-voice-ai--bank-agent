from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


Topic = Literal["credits", "deposits", "branch_locations"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4.1-mini", alias="LLM_MODEL")
    stt_model: str = Field(default="gpt-4o-mini-transcribe", alias="STT_MODEL")
    tts_model: str = Field(default="gpt-4o-mini-tts", alias="TTS_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    livekit_url: str = Field(default="ws://localhost:7880", alias="LIVEKIT_URL")
    livekit_api_key: str = Field(alias="LIVEKIT_API_KEY")
    livekit_api_secret: str = Field(alias="LIVEKIT_API_SECRET")
    livekit_room: str = Field(default="bank-support-demo", alias="LIVEKIT_ROOM")
    livekit_agent_name: str = Field(default="bank-support-agent", alias="LIVEKIT_AGENT_NAME")

    sqlite_path: Path = Field(default=Path("data/knowledge.db"), alias="SQLITE_PATH")
    search_top_k: int = Field(default=6, alias="SEARCH_TOP_K")
    max_context_chunks: int = Field(default=6, alias="MAX_CONTEXT_CHUNKS")
    min_retrieval_score: float = Field(default=0.18, alias="MIN_RETRIEVAL_SCORE")
    default_language: str = Field(default="hy", alias="DEFAULT_LANGUAGE")
    allowed_topics: str = Field(default="credits,deposits,branch_locations", alias="ALLOWED_TOPICS")
    scraper_user_agent: str = Field(
        default="ArmenianBankSupportBot/0.1 (+self-hosted LiveKit demo)",
        alias="SCRAPER_USER_AGENT",
    )

    @property
    def allowed_topic_set(self) -> set[str]:
        return {item.strip() for item in self.allowed_topics.split(",") if item.strip()}


settings = Settings()  # type: ignore[call-arg]
