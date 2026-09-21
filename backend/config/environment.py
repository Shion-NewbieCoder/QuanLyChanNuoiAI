"""Lazy environment-backed AI configuration; never validates at Django startup."""

import os
import math
from dataclasses import dataclass, field
from typing import Mapping


class AIEnvironmentError(ValueError):
    """Configuration is invalid; messages contain names, never supplied values."""


@dataclass(frozen=True)
class AIConfiguration:
    provider: str
    api_key: str = field(repr=False)


def get_ai_configuration(environ: Mapping[str, str] | None = None) -> AIConfiguration:
    """Read provider settings without selecting or calling a provider."""
    env = os.environ if environ is None else environ
    return AIConfiguration(
        provider=env.get("AI_PROVIDER", "").strip().lower(),
        api_key=env.get("AI_API_KEY", ""),
    )


@dataclass(frozen=True)
class OpenAIConfiguration:
    api_key: str = field(repr=False)
    model: str = "gpt-5.6-terra"
    timeout_seconds: float = 30
    max_retries: int = 0
    max_input_bytes: int = 65536

    def __post_init__(self):
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise AIEnvironmentError("OPENAI_API_KEY is required.")
        if not isinstance(self.model, str) or not self.model.strip():
            raise AIEnvironmentError("OPENAI_MODEL must be non-empty.")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not math.isfinite(self.timeout_seconds)
            or self.timeout_seconds <= 0
        ):
            raise AIEnvironmentError("AI_TIMEOUT_SECONDS must be finite and positive.")
        for name, value, minimum in (
            ("OPENAI_MAX_RETRIES", self.max_retries, 0),
            ("AI_MAX_INPUT_BYTES", self.max_input_bytes, 1),
        ):
            if type(value) is not int or value < minimum:
                raise AIEnvironmentError(f"{name} is invalid.")


def get_openai_configuration(environ: Mapping[str, str] | None = None) -> OpenAIConfiguration:
    env = os.environ if environ is None else environ
    try:
        timeout = float(env.get("AI_TIMEOUT_SECONDS", "30"))
        retries = int(env.get("OPENAI_MAX_RETRIES", "0"))
        limit = int(env.get("AI_MAX_INPUT_BYTES", "65536"))
    except (ValueError, TypeError, OverflowError):
        raise AIEnvironmentError("AI numeric configuration is invalid.") from None
    return OpenAIConfiguration(
        api_key=env.get("OPENAI_API_KEY", ""),
        model=env.get("OPENAI_MODEL", "gpt-5.6-terra").strip(),
        timeout_seconds=timeout,
        max_retries=retries,
        max_input_bytes=limit,
    )
