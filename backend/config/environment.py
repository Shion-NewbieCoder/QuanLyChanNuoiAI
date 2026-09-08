"""Environment-backed configuration boundary for future AI integration."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AIConfiguration:
    provider: str
    api_key: str


def get_ai_configuration() -> AIConfiguration:
    """Read provider settings without selecting or calling a provider."""
    return AIConfiguration(
        provider=os.getenv("AI_PROVIDER", ""),
        api_key=os.getenv("AI_API_KEY", ""),
    )
