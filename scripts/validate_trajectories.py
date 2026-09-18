"""Report synthetic browser trajectory ordering and evidence-field issues."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "trajectory_sample.json"


def trajectory_issues(events):
    if not isinstance(events, list):
        raise ValueError("trajectory root must be a list of event objects")
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each trajectory event must be an object")
        value = event.get("step")
        if isinstance(value, bool) or not isinstance(value, (int, str)):
            raise ValueError("step must be a positive integer")
        try:
            step = int(value)
        except ValueError:
            raise ValueError("step must be a positive integer") from None
        if step <= 0:
            raise ValueError("step must be a positive integer")
    missing_evidence = [event for event in events
                        if not isinstance(event.get("evidence"), str) or not event["evidence"].strip()]
    unordered = []
    last_step_by_task = {}
    for event in events:
        task_id = event["task_id"]
        step = int(event["step"])
        if step <= last_step_by_task.get(task_id, 0):
            unordered.append(event)
        last_step_by_task[task_id] = step
    return missing_evidence, unordered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", type=Path, nargs="?", default=DATA)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when evidence or ordering issues are found.")
    args = parser.parse_args()
    try:
        events = json.loads(args.json_path.read_text(encoding="utf-8"))
        missing_evidence, unordered = trajectory_issues(events)
    except (ValueError, KeyError, TypeError) as error:
        parser.error(f"invalid trajectory data: {error}")

    print("Trajectory validation")
    print("---------------------")
    print(f"Events: {len(events)}")
    print(f"Missing evidence: {len(missing_evidence)}")
    print(f"Ordering issues: {len(unordered)}")
    return int(args.strict and bool(missing_evidence or unordered))


if __name__ == "__main__":
    raise SystemExit(main())
