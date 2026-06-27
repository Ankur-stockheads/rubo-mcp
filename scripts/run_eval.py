"""Run the eval and (re)generate report/report.md + the SVG chart.

Modes (chosen automatically):
  * ANTHROPIC_API_KEY set + --record  -> live calls for both models, recording
    cassettes (x-api-key redacted).
  * cassettes present, no --record     -> replay the cassettes (no key needed).
  * neither                            -> heuristic baseline, clearly labelled.

Usage:
  uv run python scripts/run_eval.py            # replay cassettes, or heuristic baseline
  uv run python scripts/run_eval.py --record   # record live (needs ANTHROPIC_API_KEY)
  uv run python scripts/run_eval.py --split all
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from break_clause_analyzer.llm.client import AnthropicClient, have_api_key  # noqa: E402
from break_clause_analyzer.llm.heuristic import HeuristicClient  # noqa: E402
from eval.caseio import load_all_cases  # noqa: E402
from eval.harness import run_system  # noqa: E402
from eval.metrics import score_all  # noqa: E402
from eval.report import write_report  # noqa: E402
from eval.system import LlmSystem  # noqa: E402

MODELS = [("claude-haiku-4-5", "haiku"), ("claude-sonnet-4-6", "sonnet")]
CASSETTE_ROOT = Path(__file__).resolve().parent.parent / "eval" / "cassettes"


def _cassettes_present() -> bool:
    return all((CASSETTE_ROOT / short / "eval.yaml").exists() for _, short in MODELS)


def _vcr(short: str, record: bool):
    import vcr

    return vcr.VCR(
        cassette_library_dir=str(CASSETTE_ROOT / short),
        record_mode="once" if record else "none",
        filter_headers=[("authorization", "REDACTED"), ("x-api-key", "REDACTED")],
        match_on=["method", "scheme", "host", "port", "path", "query", "body"],
        decode_compressed_response=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true", help="record live cassettes (needs a key)")
    ap.add_argument("--split", default="eval", choices=["eval", "dev", "all"])
    args = ap.parse_args()

    cases = load_all_cases()
    if args.split != "all":
        cases = [c for c in cases if c.split == args.split]

    if args.record and not have_api_key():
        print("ERROR: --record requires ANTHROPIC_API_KEY", file=sys.stderr)
        return 2

    reports = []
    if have_api_key() or (_cassettes_present() and not args.record):
        if not have_api_key():
            # Replaying: the cassette intercepts the HTTP call, so the key is never
            # used — a dummy lets the SDK client construct.
            os.environ["ANTHROPIC_API_KEY"] = "cassette-replay-dummy"
        for model_id, short in MODELS:
            client = AnthropicClient(model_id)
            with _vcr(short, args.record).use_cassette("eval.yaml"):
                runs = run_system(LlmSystem(client), cases)
            reports.append(score_all(runs, model_id))
        if args.record:
            mode, provenance = "live + recorded cassettes", "cassettes recorded by scripts/run_eval.py --record"
        else:
            mode, provenance = "recorded cassettes (replay, no key)", "replayed from committed cassettes"
    else:
        reports.append(score_all(run_system(LlmSystem(HeuristicClient()), cases), "heuristic-baseline"))
        mode = "heuristic baseline (no ANTHROPIC_API_KEY, no cassettes)"
        provenance = (
            "deterministic heuristic — no API calls. Run `scripts/run_eval.py --record` "
            "with a key to measure claude-haiku-4-5 and claude-sonnet-4-6."
        )

    md = write_report(reports, mode, provenance, out_dir=Path(__file__).resolve().parent.parent / "report")
    print(f"wrote {md} ({mode})", file=sys.stderr)
    for r in reports:
        print(
            f"  {r.model_label}: hallucination {r.hallucination.rate:.1%} "
            f"({r.hallucination.hallucinated}/{r.hallucination.total_assertions}); "
            f"overall verdict accuracy {r.calibration.overall_accuracy:.0%}; "
            f"coverage {r.calibration.coverage:.0%}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
