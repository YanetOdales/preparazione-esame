#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

type Attempt = dict[str, Any]

DEFAULT_DATA_DIR = "/Users/yanetodales/Documents/esame medicina interna/data"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def parse_concepts(raw: str | None) -> list[str]:
    if not (raw := (raw or "").strip()):
        return []

    if raw.startswith("[") and raw.endswith("]"):
        return [str(item).strip() for item in json.loads(raw) if str(item).strip()]

    return [item.strip() for item in raw.split(",") if item.strip()]


def make_attempt(args: argparse.Namespace) -> Attempt:
    attempt: Attempt = {
        "case_code": args.case_code,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "correct": args.correct,
        "total": args.total,
    }

    if concepts := parse_concepts(args.incorrect_concepts):
        attempt["incorrect_concepts"] = concepts

    return attempt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append an exam-simulator attempt to the history JSON file."
    )
    parser.add_argument("--case-code", required=True)
    parser.add_argument("--correct", type=int, required=True)
    parser.add_argument("--total", type=int, default=10)
    parser.add_argument("--incorrect-concepts")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data_dir = Path(os.environ.get("STUDY_DATA_DIR", DEFAULT_DATA_DIR))
    data_dir.mkdir(parents=True, exist_ok=True)

    history_file = data_dir / "studio_history.json"
    history = read_json(history_file)

    attempts = [*history.get("attempts", []), make_attempt(args)]
    history_file.write_text(
        json.dumps({"attempts": attempts}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps({"success": True, "entry": attempts[-1]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()