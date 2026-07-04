#!/usr/bin/env python3
from pathlib import Path
import os
import json
import yaml
import random


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main():
    script_dir = Path(__file__).resolve().parent
    skill_root = script_dir.parent
    topics_file = skill_root / "assets" / "topics.yaml"

    data_dir = Path(
        os.environ.get(
            "STUDY_DATA_DIR",
            "/Users/yanetodales/Documents/esame medicina interna/data"
        )
    )
    history_file = data_dir / "studio_history.json"

    if not topics_file.exists():
        print(json.dumps({"error": f"File {topics_file} not found"}, ensure_ascii=False))
        return

    topics_data = yaml.safe_load(topics_file.read_text(encoding="utf-8")) or {}
    history_data = load_json(history_file)
    history = history_data.get("history", {})

    cases = []

    for topic in topics_data.get("topics", []):
        topic_name = topic.get("name")

        for case in topic.get("cases", []):
            case_id = case.get("id")
            title = case.get("title")
            diagnosis = case.get("diagnosis")
            subtopics = case.get("subtopics", [])

            case_key = case_id or title

            cases.append({
                "topic": topic_name,
                "case_id": case_id,
                "case_title": title,
                "diagnosis": diagnosis,
                "subtopics": subtopics,
                "case_key": case_key
            })

    if not cases:
        print(json.dumps({"error": "No cases found in topics.yaml"}, ensure_ascii=False))
        return

    unstudied = []
    studied = []

    for case in cases:
        topic = case["topic"]
        case_key = case["case_key"]

        case_history = history.get(topic, {}).get(case_key, {})
        session_count = case_history.get("session_count", 0)

        item = {
            "topic": topic,
            "case_id": case["case_id"],
            "case_title": case["case_title"],
            "diagnosis": case["diagnosis"],
            "subtopics": case["subtopics"],
            "subtopic": case_key,  # keeps compatibility with old update script logic
            "session_count": session_count,
        }

        if session_count == 0:
            item.update({
                "status": "unstudied",
                "last_score": None,
                "reason": "Questo caso clinico non è ancora stato affrontato. Iniziamo da qui per aumentare la copertura diagnostica."
            })
            unstudied.append(item)
        else:
            last_score = case_history.get("last_score", 0)
            total_questions = case_history.get("total_questions", 10)
            last_studied = case_history.get("last_studied", "")

            item.update({
                "status": "studied",
                "last_score": last_score,
                "total_questions": total_questions,
                "score_ratio": last_score / total_questions if total_questions > 0 else 0,
                "last_studied": last_studied,
                "reason": f"Ripassiamo questo caso per migliorare il ragionamento diagnostico precedente: {last_score}/{total_questions}."
            })
            studied.append(item)

    if unstudied:
        selected = random.choice(unstudied)
    else:
        random.shuffle(studied)
        studied.sort(key=lambda x: (x["score_ratio"], x["last_studied"]))
        selected = studied[0]
        selected["status"] = "weakest"

    selected.pop("case_key", None)

    print(json.dumps(selected, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()