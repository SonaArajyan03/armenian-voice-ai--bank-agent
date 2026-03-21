from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from pydantic import BaseModel

from bank_support.config import settings

app = FastAPI(title="Bank Support Token Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenRequest(BaseModel):
    identity: str
    room: str = settings.livekit_room


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/token")
def create_token(payload: TokenRequest) -> dict[str, str | int]:
    token = (
        api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(payload.identity)
        .with_name(payload.identity)
        .with_grants(api.VideoGrants(room_join=True, room=payload.room, can_publish=True, can_subscribe=True))
        .to_jwt()
    )
    return {"token": token, "expires_at": int(time.time()) + 3600}
