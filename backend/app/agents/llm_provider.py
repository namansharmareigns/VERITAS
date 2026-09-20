import json
import logging
import re
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMProvider:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_available(self) -> bool:
        return bool(self.settings.llm_api_key) and self.settings.llm_provider != "local"

    async def generate_json(self, system: str, user: str) -> dict[str, Any] | None:
        if not self.is_available:
            return None
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.settings.llm_model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.3,
                    },
                )
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.warning("LLM call failed: %s", e)
            return None


class EmbeddingProvider:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_available(self) -> bool:
        key = self.settings.embedding_api_key or self.settings.llm_api_key
        return bool(key) and self.settings.embedding_provider != "local"

    async def embed(self, text: str) -> list[float] | None:
        if not self.is_available:
            return self._local_embed(text)
        key = self.settings.embedding_api_key or self.settings.llm_api_key
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.settings.llm_base_url.rstrip('/')}/embeddings",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": self.settings.embedding_model, "input": text},
                )
                resp.raise_for_status()
                return resp.json()["data"][0]["embedding"]
        except Exception as e:
            logger.warning("Embedding call failed: %s", e)
            return self._local_embed(text)

    def _local_embed(self, text: str, dim: int = 64) -> list[float]:
        """Deterministic local fallback embedding for development."""
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        vec = [0.0] * dim
        for i, tok in enumerate(tokens):
            vec[i % dim] += hash(tok) % 100 / 100.0
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [round(v / norm, 6) for v in vec]
