#!/usr/bin/env python3
"""Run the internal LumenPrep adapter over isolated conversion-evaluation data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.evaluation import analyze_csv, native_result, retrieve_operational_memory


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _dataset_path(run_dir: Path, package: dict[str, object]) -> Path:
    value = package.get("dataset_csv")
    if not isinstance(value, str):
        raise ValueError("agent package has no dataset_csv")
    dataset = (run_dir / value).resolve()
    allowed = (run_dir / "datasets").resolve()
    if not _inside(dataset, allowed):
        raise ValueError("dataset_csv must resolve inside datasets/")
    return dataset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument(
        "--require-graph-rag",
        action="store_true",
        help="use the configured Neo4j runtime and fail if its retrieval falls back",
    )
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()
    packages_dir = run_dir / "agent_packages"
    output_dir = run_dir / "native_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    if not packages_dir.is_dir():
        raise SystemExit("agent_packages/ is required")

    runtime = None
    if args.require_graph_rag:
        from app.memory import create_memory_runtime

        runtime = create_memory_runtime()

    completed = 0
    try:
        for source in sorted(packages_dir.glob("scenario_*.json")):
            package = json.loads(source.read_text(encoding="utf-8"))
            if not isinstance(package, dict) or not isinstance(package.get("scenario_id"), str):
                raise SystemExit(f"invalid agent package: {source.name}")
            diagnosis = analyze_csv(_dataset_path(run_dir, package))
            memory = (
                retrieve_operational_memory(package["scenario_id"], diagnosis, runtime.service)
                if runtime is not None
                else None
            )
            destination = output_dir / source.name
            destination.write_text(
                json.dumps(
                    native_result(package["scenario_id"], diagnosis, operational_memory=memory),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            completed += 1
    finally:
        if runtime is not None:
            runtime.close()
    print(f"Created {completed} native result bundle(s) in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
