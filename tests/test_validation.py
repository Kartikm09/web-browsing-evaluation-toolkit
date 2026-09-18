import contextlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def in_memory(script, *, rows=None, events=None):
    output = io.StringIO()
    with contextlib.ExitStack() as stack:
        stack.enter_context(contextlib.redirect_stdout(output))
        stack.enter_context(patch.object(sys, "argv", [script]))
        if rows is not None:
            stack.enter_context(patch("csv.DictReader", return_value=rows))
        if events is not None:
            stack.enter_context(patch("json.loads", return_value=events))
        try:
            runpy.run_path(str(ROOT / "scripts" / script), run_name="__main__")
        except SystemExit as error:
            if error.code:
                raise
    return output.getvalue()

class TrajectoryTests(unittest.TestCase):
    def test_whitespace_is_missing_evidence(self):
        output = in_memory("validate_trajectories.py", events=[{"task_id": "t", "step": 1, "evidence": "   "}])
        self.assertIn("Missing evidence: 1", output)

    def test_interleaved_task_order_is_independent(self):
        events = [{"task_id": task, "step": step, "evidence": "source"} for task, step in [("a", 1), ("b", 1), ("a", 2), ("b", 2)]]
        output = in_memory("validate_trajectories.py", events=events)
        self.assertIn("Ordering issues: 0", output)
        self.assertIn("Missing evidence: 0", output)

    def test_report_and_strict_modes(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "events.json"
            source.write_text(json.dumps([{"task_id": "t", "step": 2, "evidence": ""}, {"task_id": "t", "step": 1, "evidence": "source"}]))
            args = [sys.executable, str(ROOT / "scripts/validate_trajectories.py"), str(source)]
            report = subprocess.run(args, capture_output=True, text=True, cwd=ROOT, timeout=10)
            strict = subprocess.run([*args, "--strict"], capture_output=True, text=True, cwd=ROOT, timeout=10)
            self.assertEqual(report.returncode, 0)
            self.assertEqual(strict.returncode, 1)
            self.assertEqual(report.stdout, strict.stdout)
            self.assertIn("Missing evidence: 1", report.stdout)
            self.assertIn("Ordering issues: 1", report.stdout)

    def test_malformed_shape_is_a_clear_data_error(self):
        invalid_inputs = [{}, [None], [{"task_id": "t", "step": True, "evidence": "source"}],
                          [{"task_id": "t", "step": 1.5, "evidence": "source"}]]
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "events.json"
            for events in invalid_inputs:
                with self.subTest(events=events):
                    source.write_text(json.dumps(events))
                    result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_trajectories.py"), str(source), "--strict"], text=True, capture_output=True, cwd=ROOT, timeout=10)
                    self.assertEqual(result.returncode, 2)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn("invalid trajectory data", result.stderr)

    def test_positive_integer_strings_remain_supported(self):
        output = in_memory("validate_trajectories.py", events=[{"task_id": "t", "step": "1", "evidence": "source"}])
        self.assertIn("Ordering issues: 0", output)

    def test_empty_task_summary_is_explicit(self):
        output = in_memory("summarize_browser_tasks.py", rows=[])
        self.assertIn("Tasks: 0", output)
        self.assertIn("Average score: N/A", output)

if __name__ == "__main__":
    unittest.main()
