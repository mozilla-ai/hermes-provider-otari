<p align="center">
  <img src="assets/otari-logo.svg" width="320" alt="Otari logo"/>
</p>

# Otari provider for Hermes Agent

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) model-provider plugin for
[Otari](https://github.com/mozilla-ai/otari), the open-source LLM gateway from Mozilla.ai. Hermes
talks to Otari over its OpenAI-compatible API, so one Otari key reaches every model your gateway
serves, with Otari's budgets, routing and usage tracking applied to each call.

The plugin registers one provider, `otari`, and nothing else: no tools, hooks or commands.

## Install

```bash
hermes plugins install otari
```

Then set your key and pick the provider:

```bash
hermes config set OTARI_API_KEY <your-otari-key>
hermes chat --provider otari -m openai/gpt-4o
```

`hermes model` also lists Otari, and its model picker reads the models your key can use from the
gateway's `GET /api/v1/models`.

## Which gateway

| Gateway | `OTARI_BASE_URL` |
| --- | --- |
| otari.ai | not needed (defaults to `https://api.otari.ai/api/v1`) |
| otari.ai, EU region | `https://eu.api.otari.ai/api/v1` |
| Your own Otari | your gateway's URL plus `/api/v1`, for example `http://localhost:8000/api/v1` |

An EU key sent to `api.otari.ai` is answered with `421 Misdirected Request`; set `OTARI_BASE_URL`
to the EU host.

## Choosing a model

The model id is whatever your gateway's catalog lists: a routed id such as `openai/gpt-4o`, a pinned
`provider:model` selector such as `anthropic:claude-sonnet-4-6`, or the name of a routing policy.

## Reasoning effort

Hermes's `--reasoning` level (or `agent.reasoning_effort`) is sent as `reasoning_effort`. `max` is
sent as `xhigh`, the highest level Otari accepts. When reasoning is off or unset, the field is left
out and the model's own default applies, because Otari does not accept `none`.

## What it does on your machine

- Network: requests go only to the Otari gateway you configure, through Hermes's own HTTP client.
- Credentials: `OTARI_API_KEY` is read by Hermes. The plugin stores nothing and reads no files.
- No background processes, shell commands or telemetry.

## Development

```bash
python3 -m unittest discover -s tests -v       # offline tests, no Hermes needed
hermes plugins validate otari --install-deps   # the catalog's admission check
```

Requires Hermes Agent 0.22.5 or later.

## License

Apache-2.0, the same license as [Otari](https://github.com/mozilla-ai/otari). See [LICENSE](LICENSE).
