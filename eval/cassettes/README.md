# Cassettes

Recorded Anthropic API responses, one cassette set per model
(`haiku/`, `sonnet/`). They make the eval **reproducible with no API key**: the
scoring harness replays them instead of calling the live API, so a reviewer gets
the published numbers in under two minutes.

## How they are produced

`scripts/run_eval.py` wraps each model's API calls in a VCR.py cassette:

```bash
# Record (needs ANTHROPIC_API_KEY) — writes haiku/eval.yaml and sonnet/eval.yaml
uv run python scripts/run_eval.py --record

# Replay (no key needed) — reads the cassettes, recomputes the report
uv run python scripts/run_eval.py
```

## Safety + reproducibility rules (enforced in code)

- **`x-api-key` is redacted** before anything is written, so no key leaks into this
  public repo. (Anthropic authenticates with `x-api-key`, not `authorization`.)
- **Requests match on body**, so each distinct prompt maps to its own recorded
  response — different cases can't collide on one cassette.
- **Replay never calls the network.** A missing cassette is an error, not a silent
  live call.
- `temperature=0` is *not* a determinism guarantee from the API, so the cassettes —
  not the temperature — are what make the published number reproducible. Each
  cassette is stamped with the model id; the report records the last live-record date.

> If these directories are empty apart from `.gitkeep`, no live recording has been
> made yet — run with a key as above. Until then the eval falls back to the
> heuristic baseline, clearly labelled as such in the report.
