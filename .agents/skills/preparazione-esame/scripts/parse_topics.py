#!/usr/bin/env python3
from pathlib import Path
import json
import yaml
import argparse


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_topics(data: dict) -> list[str]:
    errors = []

    topics = data.get("topics")
    if not isinstance(topics, list):
        return ["Il file YAML deve contenere una lista 'topics'."]

    seen_case_ids = set()

    for topic_index, topic in enumerate(topics, start=1):
        topic_name = topic.get("name")

        if not topic_name:
            errors.append(f"Topic #{topic_index}: manca il campo 'name'.")

        cases = topic.get("cases")
        if not isinstance(cases, list) or not cases:
            errors.append(f"Topic '{topic_name}': manca una lista valida 'cases'.")
            continue

        for case_index, case in enumerate(cases, start=1):
            prefix = f"Topic '{topic_name}', caso #{case_index}"

            case_id = case.get("id")
            title = case.get("title")
            diagnosis = case.get("diagnosis")
            subtopics = case.get("subtopics")

            if not case_id:
                errors.append(f"{prefix}: manca 'id'.")
            elif case_id in seen_case_ids:
                errors.append(f"{prefix}: id duplicato '{case_id}'.")
            else:
                seen_case_ids.add(case_id)

            if not title:
                errors.append(f"{prefix}: manca 'title'.")

            if not diagnosis:
                errors.append(f"{prefix}: manca 'diagnosis'.")

            if not isinstance(subtopics, list) or not subtopics:
                errors.append(f"{prefix}: manca una lista valida 'subtopics'.")

    return errors


def flatten_cases(data: dict) -> list[dict]:
    flattened = []

    for topic in data.get("topics", []):
        topic_name = topic.get("name")

        for case in topic.get("cases", []):
            flattened.append({
                "topic": topic_name,
                "case_id": case.get("id"),
                "case_title": case.get("title"),
                "diagnosis": case.get("diagnosis"),
                "subtopics": case.get("subtopics", [])
            })

    return flattened


def main():
    parser = argparse.ArgumentParser(
        description="Parse and validate topics.yaml for the clinical case simulator."
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Path opzionale al file topics.yaml"
    )
    parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="Formato output"
    )

    args = parser.parse_args()

    if args.file:
        topics_file = Path(args.file).expanduser().resolve()
    else:
        script_dir = Path(__file__).resolve().parent
        skill_root = script_dir.parent
        topics_file = skill_root / "assets" / "topics.yaml"

    try:
        data = load_yaml(topics_file)
        errors = validate_topics(data)
        cases = flatten_cases(data)

        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "topics_count": len(data.get("topics", [])),
            "cases_count": len(cases),
            "cases": cases
        }

        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if result["valid"]:
                print("YAML valido.")
            else:
                print("YAML non valido.")

            print(f"Topics: {result['topics_count']}")
            print(f"Casi clinici: {result['cases_count']}")

            if errors:
                print("\nErrori:")
                for error in errors:
                    print(f"- {error}")

    except Exception as exc:
        print(json.dumps({
            "valid": False,
            "error": str(exc)
        }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```
