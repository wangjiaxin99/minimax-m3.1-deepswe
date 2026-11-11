import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("summary", Path(__file__).parents[1] / "scripts/summarize.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class SummaryTests(unittest.TestCase):
    def test_deduplicate_responses_and_classify_tool_timeout(self):
        response = {"object": "response", "id": "r1", "incomplete_details": {"reason": "max_output_tokens"}}
        messages = [response, {"extra": {"response": response}},
                    {"type": "function_call_output", "call_id": "c1", "extra": {"exception_info": "timed out after 30 seconds"}},
                    {"type": "function_call_output", "call_id": "c1", "extra": {"exception_info": "timed out after 30 seconds"}}]
        result = summary.trajectory_diagnostics({"messages": messages})
        self.assertEqual(result["truncated_responses"], 1)
        self.assertEqual(result["tool_timeout_30s_calls"], 1)

    def test_missing_reward_keeps_fixed_denominator(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            (job / "result.json").write_text(json.dumps({"started_at": "2026-11-10T00:00:00", "finished_at": "2026-11-10T00:01:00"}))
            for i, reward in enumerate((1, 0, None)):
                trial = job / f"trial{i}"
                trial.mkdir()
                (trial / "result.json").write_text(json.dumps({"task_name": f"task{i}", "finished_at": "2026-11-10T00:01:00", "verifier_result": {"rewards": {"reward": reward}}}))
            result = summary.audit_job(job, 3)
            self.assertEqual(result["passed"], 1)
            self.assertEqual(result["expected"], 3)
            self.assertEqual(result["missing_rewards"], 1)
            self.assertAlmostEqual(result["pass_percent_fixed_denominator"], 100 / 3)
            with self.assertRaises(ValueError):
                summary.audit_job(job, 4)

    def test_three_attempt_job_averages_all_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            (job / "result.json").write_text(json.dumps({"finished_at": "2026-11-10T00:01:00"}))
            for i, reward in enumerate((1, 0, None)):
                trial = job / f"attempt{i}"
                trial.mkdir()
                (trial / "result.json").write_text(json.dumps({"task_name": "same-task", "finished_at": "2026-11-10T00:01:00", "verifier_result": {"rewards": {"reward": reward}}}))
            result = summary.audit_job(job, 3, attempts_per_task=3)
            self.assertEqual(result["passed"], 1)
            self.assertEqual(result["expected"], 3)
            self.assertAlmostEqual(result["pass_percent_fixed_denominator"], 100 / 3)
            with self.assertRaises(ValueError):
                summary.audit_job(job, 3, attempts_per_task=1)


if __name__ == "__main__":
    unittest.main()
