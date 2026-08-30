"""Run the OpenAI-backed evaluator in an isolated local Lumen instance."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.config import settings
from app.evaluation import CaseEvaluator, InProcessApi, OpenAIResponsesPlanner
from app.ingestion import storage
from app.streaming import reset_transaction_pipeline
from main import create_app


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--focus", default="")
    args = parser.parse_args()
    if not settings.openai_api_key:
        parser.error("OPENAI_API_KEY is missing. Add it to .env before running the evaluator.")
    context = (ROOT / "avaliacao.md").read_text(encoding="utf-8")[:12_000]
    # A QA run must never create records in the user's persistent demo database.
    settings.duckdb_path = ":memory:"
    storage.reset_connection()
    reset_transaction_pipeline()
    with TestClient(create_app(settings)) as client:
        evaluator = CaseEvaluator(
            api=InProcessApi(client),
            planner=OpenAIResponsesPlanner(api_key=settings.openai_api_key or "", model=settings.openai_model),
            case_context=context,
            truth_root=ROOT,
        )
        try:
            report = evaluator.run(focus=args.focus)
        except RuntimeError as error:
            parser.exit(1, f"Evaluator could not finish: {error}\n")
    for probe in report.probes:
        print(f"{'PASS' if probe.passed else 'FAIL'} {probe.name}: {probe.evidence}")
    print(f"\nModel: {report.model}\n\n{report.feedback}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
