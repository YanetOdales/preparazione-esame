#!/usr/bin/env python3
from pathlib import Path
import os
import json
import argparse
from datetime import datetime, timezone
from typing import List, Union


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def parse_incorrect_concepts(raw: Union[str, None]) -> List[str]:
    if not raw:
        return []

    cleaned = raw.strip()

    if cleaned.startswith("[") and cleaned.endswith("]"):
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except Exception:
            pass

    return [item.strip() for item in raw.split(",") if item.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Update study history with clinical case assessment metadata."
    )
    parser.add_argument("--topic", required=True, help="Main topic category")
    parser.add_argument(
        "--subtopic",
        required=True,
        help="Case key, case title, case id, or old-style subtopic"
    )
    parser.add_argument("--score", type=int, required=True, help="Score obtained in the assessment")
    parser.add_argument("--total", type=int, default=10, help="Total number of questions")
    parser.add_argument("--incorrect-concepts", help="Comma-separated list or JSON list of wrong concepts")

    parser.add_argument("--case-id", help="Optional clinical case id")
    parser.add_argument("--case-title", help="Optional clinical case title")
    parser.add_argument("--diagnosis", help="Optional expected diagnosis")
    parser.add_argument("--missed-diagnosis", help="Optional diagnosis proposed incorrectly by the student")
    parser.add_argument("--reasoning-feedback", help="Optional feedback on diagnostic reasoning")

    args = parser.parse_args()

    data_dir = Path(
        os.environ.get(
            "STUDY_DATA_DIR",
            "/Users/yanetodales/Documents/esame medicina interna/data"
        )
    )
    data_dir.mkdir(parents=True, exist_ok=True)

    history_file = data_dir / "studio_history.json"
    history_data = load_json(history_file)

    history_data.setdefault("history", {})
    history = history_data["history"]

    history.setdefault(args.topic, {})

    case_key = args.case_id or args.subtopic

    if case_key not in history[args.topic]:
        history[args.topic][case_key] = {
            "session_count": 0,
            "last_score": 0,
            "total_questions": 0,
            "last_studied": "",
            "case_id": args.case_id,
            "case_title": args.case_title or args.subtopic,
            "diagnosis": args.diagnosis,
            "detailed_sessions": []
        }

    case_history = history[args.topic][case_key]

    incorrect_list = parse_incorrect_concepts(args.incorrect_concepts)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    case_history["session_count"] += 1
    case_history["last_score"] = args.score
    case_history["total_questions"] = args.total
    case_history["last_studied"] = timestamp

    if args.case_id:
        case_history["case_id"] = args.case_id
    if args.case_title:
        case_history["case_title"] = args.case_title
    if args.diagnosis:
        case_history["diagnosis"] = args.diagnosis

    session_record = {
        "timestamp": timestamp,
        "score": args.score,
        "total": args.total,
        "incorrect_concepts": incorrect_list,
        "missed_diagnosis": args.missed_diagnosis,
        "reasoning_feedback": args.reasoning_feedback
    }

    case_history.setdefault("detailed_sessions", [])
    case_history["detailed_sessions"].append(session_record)

    history_file.write_text(
        json.dumps(history_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps({
        "success": True,
        "updated": {
            args.topic: {
                case_key: case_history
            }
        }
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()