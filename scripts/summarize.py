"""Read native final trial rewards and diagnostics; never rerun or change grades."""
import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re


def trajectory_diagnostics(trajectory):
    responses = {}
    timeouts = {}
    for message in trajectory.get("messages", []):
        if message.get("object") == "response" and message.get("id"):
            responses[message["id"]] = message
        extra = message.get("extra") or {}
        response = extra.get("response") if isinstance(extra, dict) else None
        if isinstance(response, dict) and response.get("id"):
            responses[response["id"]] = response
        if message.get("type") == "function_call_output" and isinstance(extra, dict):
            match = re.search(r"timed out after ([0-9.]+) seconds", str(extra.get("exception_info", "")))
            if match:
                timeouts[message.get("call_id")] = float(match.group(1))
    truncated = []
    for response in responses.values():
        if (response.get("incomplete_details") or {}).get("reason") == "max_output_tokens":
            usage = response.get("usage") or {}
            truncated.append({"response_id": response["id"], "input_tokens": usage.get("input_tokens"),
                              "output_tokens": usage.get("output_tokens"),
                              "effective_max_output_tokens": response.get("max_output_tokens")})
    return {"truncated_responses": len(truncated), "truncated_details": truncated,
            "agent_exit_status": (trajectory.get("info") or {}).get("exit_status"),
            "response_count": len(responses),
            "max_input_tokens": max(((r.get("usage") or {}).get("input_tokens") or 0 for r in responses.values()), default=0),
            "max_output_tokens": max(((r.get("usage") or {}).get("output_tokens") or 0 for r in responses.values()), default=0),
            "tool_timeout_calls": len(timeouts),
            "tool_timeout_30s_calls": sum(t == 30 for t in timeouts.values())}


def audit_job(job, expected, allow_incomplete=False, attempts_per_task=1):
    job_result = json.loads((job / "result.json").read_text()) if (job / "result.json").exists() else {}
    trials = []
    names = Counter()
    for file in sorted(job.glob("*/result.json")):
        result = json.loads(file.read_text())
        if not result.get("finished_at"):
            continue
        task = result["task_name"]
        names[task] += 1
        if names[task] > attempts_per_task:
            raise ValueError(f"Too many final trials for {task}; expected {attempts_per_task}")
        trial = file.parent
        reward = ((result.get("verifier_result") or {}).get("rewards") or {}).get("reward")
        trajectory_file = trial / "agent/mini-swe-agent.trajectory.json"
        trajectory = json.loads(trajectory_file.read_text()) if trajectory_file.exists() else {}
        patch = trial / "artifacts/model.patch"
        item = {"task": task, "trial": trial.name, "reward": reward,
                "exception_type": (result.get("exception_info") or {}).get("exception_type"),
                "missing_trajectory": not trajectory_file.exists(), "missing_patch": not patch.exists(),
                "empty_patch": patch.exists() and patch.stat().st_size == 0}
        item.update(trajectory_diagnostics(trajectory))
        trials.append(item)
    complete = (len(trials) == expected and bool(job_result.get("finished_at"))
                and all(n == attempts_per_task for n in names.values())
                and not any(t["exception_type"] == "CancelledError" for t in trials))
    if not complete and not allow_incomplete:
        raise ValueError(f"Incomplete job {job}: {len(trials)}/{expected}; use --allow-incomplete for progress")
    if len(trials) > expected:
        raise ValueError("More trials than expected")
    start, end = job_result.get("started_at"), job_result.get("finished_at")
    seconds = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() if start and end else None
    passed = sum(t["reward"] == 1 for t in trials)
    return {"completed": len(trials), "expected": expected, "complete": complete,
            "passed": passed, "pass_percent_fixed_denominator": passed / expected * 100,
            "missing_rewards": sum(t["reward"] is None for t in trials), "wall_seconds": seconds,
            "exception_types": dict(Counter(t["exception_type"] for t in trials if t["exception_type"])),
            "agent_exit_status": dict(Counter(t["agent_exit_status"] for t in trials if t["agent_exit_status"])),
            "repeated_format_error_trials": sum(t["agent_exit_status"] == "RepeatedFormatError" for t in trials),
            "empty_patches": sum(t["empty_patch"] for t in trials),
            "missing_patches": sum(t["missing_patch"] for t in trials),
            "missing_trajectories": sum(t["missing_trajectory"] for t in trials),
            "truncated_responses": sum(t["truncated_responses"] for t in trials),
            "trials_with_truncation": sum(bool(t["truncated_responses"]) for t in trials),
            "tool_timeout_30s_calls": sum(t["tool_timeout_30s_calls"] for t in trials),
            "trials_with_tool_timeout_30s": sum(bool(t["tool_timeout_30s_calls"]) for t in trials),
            "trials": trials}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    rounds = []
    attempts = manifest.get("attempts_per_job", 1)
    for index, relative in enumerate(manifest["jobs"], 1):
        row = audit_job(args.manifest.parent / relative, manifest["tasks_per_round"] * attempts,
                        args.allow_incomplete, attempts_per_task=attempts)
        row["job_index"] = index
        rounds.append(row)
    passed = sum(r["passed"] for r in rounds)
    expected = sum(r["expected"] for r in rounds)
    report = {"format": manifest["format"], "complete": all(r["complete"] for r in rounds),
              "passed": passed, "expected": expected, "pass_percent": passed / expected * 100,
              "jobs": rounds}
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized)
    for r in rounds:
        print(f"job{r['job_index']}: {r['completed']}/{r['expected']} finished, {r['passed']} passed, "
              f"truncations={r['truncated_responses']}, missing rewards={r['missing_rewards']}")
    print(f"{manifest['format']}: {passed}/{expected} = {report['pass_percent']:.2f}% (complete={report['complete']})")


if __name__ == "__main__":
    main()
