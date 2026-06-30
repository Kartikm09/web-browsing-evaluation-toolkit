"""Summarize synthetic browser task evaluation rows."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "browser_tasks.csv"
with DATA.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

scores = [int(row["score"]) for row in rows]
issues = Counter(row["issue_type"] for row in rows)
print("Browser task summary")
print("--------------------")
print(f"Tasks: {len(rows)}")
print(f"Average score: {sum(scores) / len(scores):.2f}")
for issue, count in issues.most_common():
    print(f"- {issue}: {count}")
