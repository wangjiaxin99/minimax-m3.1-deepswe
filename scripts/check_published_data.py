"""Check published trial metadata, totals and CSV against the historical audit."""
import csv
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "data/latest-results.json").read_text())
    expected = {"mxfp8": ([87, 83, 79], 5, 1, 637), "mxfp4": ([76, 82, 78], 9, 2, 583)}
    with (root / "data/trials.csv").open() as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 678
    csv_by_trial = {(r["format"], int(r["round"]), r["trial"]): r for r in rows}
    assert len(csv_by_trial) == 678
    for model in record["models"]:
        fmt = model["format"]
        passed, truncated, affected, timeouts = expected[fmt]
        assert [r["passed"] for r in model["rounds"]] == passed
        assert sum(r["truncated_responses"] for r in model["rounds"]) == truncated
        assert sum(r["trials_with_truncation"] for r in model["rounds"]) == affected
        assert sum(r["tool_timeout_calls"] for r in model["rounds"]) == timeouts
        for r in model["rounds"]:
            trials = r["trials"]
            assert len(trials) == 113
            assert len({t["task"] for t in trials}) == 113
            assert sum(t["reward"] == 1 for t in trials) == r["passed"]
            assert sum(t["reward"] is None for t in trials) == r["missing_rewards"]
            assert sum(t["truncated_responses"] for t in trials) == r["truncated_responses"]
            assert sum(t["tool_timeout_30s_calls"] for t in trials) == r["tool_timeout_calls"]
            for t in trials:
                row = csv_by_trial[fmt, r["round"], t["trial"]]
                assert row["result_sha256"] == t["result_sha256"]
                assert row["reward"] == ("" if t["reward"] is None else str(t["reward"]))
                assert "/home/" not in json.dumps(t) and "exception_traceback" not in t
        print(f"{fmt}: {sum(passed)}/339; {truncated} truncated responses; metadata checked")


if __name__ == "__main__":
    main()
