#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import random
import tomllib
from collections import defaultdict
from pathlib import Path
from typing import Any

Case = dict[str, Any]
Cases = dict[str, Case]
Scores = dict[str, list[int]]

DEFAULT_DATA_DIR = "/data/esami"

REASONS = {
    "unattempted": "This case has not been attempted yet.",
    "weighted": "This case was selected with probability weighted by your last score.",
}

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_cases(path: Path) -> Cases:
    return {
        str(case["number"]): {
            "title": case["title"],
            "section": case["section"],
            "objectives": case["objectives"],
        }
        for case in read_toml(path)["cases"]
    }


def build_scores(history: dict[str, Any]) -> Scores:
    scores: Scores = defaultdict(list)

    for attempt in history.get("attempts", []):
        case_id = str(attempt["case_code"]).strip()
        scores[case_id].append(round(10 * attempt["correct"] / attempt["total"]))

    return dict(scores)


def pick_unattempted_case(cases: Cases, scores: Scores) -> tuple[str, str]:
    case_id = random.choice([case_id for case_id in cases if case_id not in scores])
    return case_id, REASONS["unattempted"]


def case_weight(last_score: int) -> float:
    return (11 - last_score) ** 2


def pick_weighted_case(cases: Cases, scores: Scores) -> tuple[str, str]:
    case_ids = list(cases)

    weights = [
        case_weight(scores[case_id][-1])
        for case_id in case_ids
    ]

    return random.choices(case_ids, weights=weights, k=1)[0], REASONS["weighted"]


def select_case(cases: Cases, scores: Scores) -> dict[str, Any]:
    picker = pick_unattempted_case if set(cases) - set(scores) else pick_weighted_case
    case_id, reason = picker(cases, scores)
    case = cases[case_id]

    return {
        "case_id": case_id,
        "case_title": case["title"],
        "section": case["section"],
        "objectives": case["objectives"],
        "reason": reason,
    }


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    data_dir = Path(os.environ.get("EXAM_RESULTS_PATH", DEFAULT_DATA_DIR))
    data_dir.mkdir(parents=True, exist_ok=True)

    cases = load_cases(root / "assets" / "topics.toml")
    scores = build_scores(read_json(data_dir / "studio_history.json"))

    print(json.dumps(select_case(cases, scores), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()