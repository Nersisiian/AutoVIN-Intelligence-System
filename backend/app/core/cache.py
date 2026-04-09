from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings


class Cache:
    def __init__(self, client: redis.Redis):
        self._client = client

    async def get_json(self, key: str) -> dict[str, Any] | None:
        raw = await self._client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        await self._client.set(key, json.dumps(value), ex=ttl_seconds)


redis_client: redis.Redis = redis.from_url(
    settings.redis_url, encoding="utf-8", decode_responses=True
)
cache = Cache(redis_client)
