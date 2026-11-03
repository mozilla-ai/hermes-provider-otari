"""Offline tests for the Otari provider profile."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hermes_stub import load_plugin  # noqa: E402


class RegistrationTest(unittest.TestCase):
    def setUp(self):
        self.module, self.registered = load_plugin()
        self.profile = self.registered["otari"]

    def test_registers_exactly_one_provider_on_import(self):
        self.assertEqual(list(self.registered), ["otari"])

    def test_points_at_the_hosted_gateway_over_chat_completions(self):
        self.assertEqual(self.profile.base_url, "https://api.otari.ai/api/v1")
        self.assertEqual(self.profile.api_mode, "chat_completions")
        self.assertEqual(self.profile.auth_type, "api_key")

    def test_reads_the_same_env_vars_as_other_otari_integrations(self):
        # Hermes treats the ``_BASE_URL`` entry as the endpoint override.
        self.assertEqual(self.profile.env_vars, ("OTARI_API_KEY", "OTARI_BASE_URL"))

    def test_leaves_models_to_the_live_catalog(self):
        self.assertEqual(self.profile.fallback_models, ())
        self.assertEqual(self.profile.default_aux_model, "")


class ReasoningTest(unittest.TestCase):
    def setUp(self):
        module, registered = load_plugin()
        self.profile = registered["otari"]

    def extras(self, reasoning_config):
        return self.profile.build_api_kwargs_extras(reasoning_config=reasoning_config, model="openai/gpt-5")

    def test_passes_a_supported_effort_through_at_top_level(self):
        for effort in ("minimal", "low", "medium", "high", "xhigh"):
            with self.subTest(effort=effort):
                self.assertEqual(
                    self.extras({"enabled": True, "effort": effort}), ({}, {"reasoning_effort": effort})
                )

    def test_normalizes_case_and_whitespace(self):
        self.assertEqual(self.extras({"effort": " High "}), ({}, {"reasoning_effort": "high"}))

    def test_clamps_max_to_xhigh(self):
        self.assertEqual(self.extras({"effort": "max"}), ({}, {"reasoning_effort": "xhigh"}))

    def test_never_sends_none(self):
        # Otari answers ``reasoning_effort: "none"`` with a 400 (hermes-agent #114460).
        for config in ({"effort": "none"}, {"enabled": False}, {"enabled": False, "effort": "high"}):
            with self.subTest(config=config):
                self.assertEqual(self.extras(config), ({}, {}))

    def test_omits_the_field_when_unset_or_unknown(self):
        for config in (None, {}, {"enabled": True}, {"effort": "turbo"}, "high"):
            with self.subTest(config=config):
                self.assertEqual(self.extras(config), ({}, {}))


if __name__ == "__main__":
    unittest.main()
