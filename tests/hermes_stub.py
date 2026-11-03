"""A stand-in for Hermes's ``providers`` package, so the plugin loads without Hermes.

It mirrors only the surface the plugin touches: ``ProviderProfile`` as a dataclass
with the fields the plugin sets, and ``register_provider``. CI also runs
``hermes plugins validate`` against a real Hermes, which catches drift here.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PLUGIN_INIT = Path(__file__).resolve().parent.parent / "otari" / "__init__.py"


@dataclass
class ProviderProfile:
    name: str
    api_mode: str = "chat_completions"
    aliases: tuple = ()
    display_name: str = ""
    description: str = ""
    signup_url: str = ""
    env_vars: tuple = ()
    base_url: str = ""
    auth_type: str = "api_key"
    fallback_models: tuple = ()
    default_aux_model: str = ""

    def build_api_kwargs_extras(
        self, *, reasoning_config: dict | None = None, **context: Any
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return {}, {}


def load_plugin() -> tuple[types.ModuleType, dict[str, ProviderProfile]]:
    """Import the plugin fresh against the stub; return it and what it registered."""
    registered: dict[str, ProviderProfile] = {}

    providers = types.ModuleType("providers")
    providers.register_provider = lambda profile: registered.__setitem__(profile.name, profile)
    base = types.ModuleType("providers.base")
    base.ProviderProfile = ProviderProfile
    providers.base = base
    sys.modules["providers"] = providers
    sys.modules["providers.base"] = base

    spec = importlib.util.spec_from_file_location("otari_plugin_under_test", PLUGIN_INIT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, registered
