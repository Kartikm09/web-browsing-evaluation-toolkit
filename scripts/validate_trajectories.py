"""Validate synthetic browser trajectory ordering and evidence fields."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "trajectory_sample.json"
events = json.loads(DATA.read_text(encoding="utf-8"))

missing_evidence = [event for event in events if not event.get("evidence")]
unordered = []
last_step_by_task = {}
for event in events:
    task_id = event["task_id"]
    step = int(event["step"])
    if step <= last_step_by_task.get(task_id, 0):
        unordered.append(event)
    last_step_by_task[task_id] = step

print("Trajectory validation")
print("---------------------")
print(f"Events: {len(events)}")
print(f"Missing evidence: {len(missing_evidence)}")
print(f"Ordering issues: {len(unordered)}")
