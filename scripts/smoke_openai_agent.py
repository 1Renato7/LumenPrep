"""Run one real, non-persistent OpenAI smoke test for the diagnostic agent.

Set ``OPENAI_API_KEY`` only in the ignored local ``.env`` file or process
environment. This script never prints the key and sends only the repository's
synthetic Incident fixture to the configured OpenAI client.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.agent import DiagnosticAgentService, OpenAISuggestionClient
from app.config import settings
from app.incidents import Incident


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "contracts" / "fixtures" / "incident-mastercard-recurrence.json"
DECLINE_PROFILE = {"NO_DECLINE": 98, "PROVIDER_TIMEOUT": 96, "DO_NOT_HONOR": 46}


def main() -> int:
    if not settings.openai_api_key:
        print("OPENAI_API_KEY is not configured locally; no request was sent.")
        return 2

    incident = Incident.model_validate(json.loads(FIXTURE.read_text(encoding="utf-8")))
    service = DiagnosticAgentService()
    if not isinstance(service.client, OpenAISuggestionClient):
        print("The configured agent did not select OpenAISuggestionClient; no request was sent.")
        return 2

    suggestion = service.suggest_for_incident(
        incident,
        decline_profile=DECLINE_PROFILE,
        persist=False,
    )
    summary = {
        "status": suggestion.status,
        "model_version": suggestion.model_version,
        "configured_reasoning_effort": settings.openai_reasoning_effort,
        "suggested_category": suggestion.suggested_category,
        "reason_count": len(suggestion.reasons),
        "action_count": len(suggestion.recommended_actions),
        "limitations": suggestion.limitations,
    }
    print(json.dumps(summary, indent=2))
    return 0 if suggestion.status == "SUGGESTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
