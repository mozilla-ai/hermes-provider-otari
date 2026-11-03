"""Otari model provider for Hermes Agent.

Otari is an OpenAI-compatible LLM gateway, so requests use Hermes's
``chat_completions`` wire against ``<gateway>/api/v1``. The model list comes
from the gateway's own ``GET /api/v1/models``, which answers only what the
key may use.
"""

from __future__ import annotations

from typing import Any

from providers import register_provider
from providers.base import ProviderProfile

HOSTED_BASE_URL = "https://api.otari.ai/api/v1"

# Otari rejects ``none``, so "reasoning off" is expressed by omitting the field.
_WIRE_EFFORTS = ("minimal", "low", "medium", "high", "xhigh")
_EFFORT_ALIASES = {"max": "xhigh"}


def wire_effort(reasoning_config: dict | None) -> str | None:
    """The ``reasoning_effort`` value to send, or None to leave the route's default."""
    if not isinstance(reasoning_config, dict) or reasoning_config.get("enabled") is False:
        return None
    effort = str(reasoning_config.get("effort") or "").strip().lower()
    effort = _EFFORT_ALIASES.get(effort, effort)
    return effort if effort in _WIRE_EFFORTS else None


class OtariProfile(ProviderProfile):
    """Otari gateway: top-level ``reasoning_effort``, never ``none``."""

    def build_api_kwargs_extras(
        self, *, reasoning_config: dict | None = None, **context: Any
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        effort = wire_effort(reasoning_config)
        return ({}, {"reasoning_effort": effort}) if effort else ({}, {})


otari = OtariProfile(
    name="otari",
    aliases=("otari-ai", "otari.ai"),
    display_name="Otari",
    description="Otari LLM gateway: one key for every provider, with budgets and usage tracking",
    signup_url="https://otari.ai",
    env_vars=("OTARI_API_KEY", "OTARI_BASE_URL"),
    base_url=HOSTED_BASE_URL,
    auth_type="api_key",
    # Model ids depend on the providers each gateway is configured with, so
    # auxiliary tasks run on the main model and the picker uses the live list.
    default_aux_model="",
    fallback_models=(),
)

register_provider(otari)
