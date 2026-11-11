"""Capture controller versions and dedicated daemon state, without credentials."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import subprocess


def output(*command):
    return subprocess.check_output(command, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(os.environ["REPO_DIR"])
    tasks = Path(os.environ["TASKS_DIR"]).parent
    record = {
        "python": platform.python_version(),
        "packages": {p: metadata.version(p) for p in ("datacurve-pier", "harbor")},
        "task_commit": output("git", "-C", str(tasks), "rev-parse", "HEAD"),
        "task_diff": output("git", "-C", str(tasks), "diff", "--stat"),
        "docker": output("docker", "version", "--format", "{{json .}}"),
        "compose": output("docker", "compose", "version", "--short"),
        "daemon": json.loads(output("docker", "info", "--format", "{{json .}}")),
        "patch_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root / "patches").glob("*.patch"))},
        "mini_swe_version": "2.4.5",
        "agent_extra_packages": ["litellm[mcp]==1.108.3", "mcp==2.3.0"],
        "evaluation": {"model_format": os.environ["MODEL_FORMAT"], "concurrency": 64,
                       "context_tokens": 524288, "max_output_tokens": 65536,
                       "temperature": 1.0, "top_p": 0.95, "reasoning_effort": "max",
                       "n_attempts": 3, "max_retries": 2},
    }
    if record["task_commit"] != "0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea" or record["task_diff"]:
        raise RuntimeError("Task source differs from pinned benchmark")
    args.output.write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    main()
