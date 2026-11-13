"""Assert that a fault-injection run failed for the right reasons.

Each corrupted row written by `pipeline/ingest.py --inject-faults` must be caught
by its own check, at the right severity, and the bad data must not reach the marts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPECTED = {
    # test name (prefix)                                    : expected status
    "source_not_null_usgs_earthquakes_id": "fail",            # missing event id
    "source_text_numeric_in_range_usgs_earthquakes_mag": "fail",       # magnitude 12.4
    "source_text_numeric_in_range_usgs_earthquakes_latitude": "fail",  # latitude 123.45
    "assert_no_future_events_in_source": "fail",              # event 3 days in the future
    "source_accepted_values_usgs_earthquakes_type": "warn",   # unknown event type (warn only)
}


def main() -> int:
    results = json.loads(Path("target/run_results.json").read_text())["results"]
    by_name = {r["unique_id"].split(".")[2]: r for r in results}
    problems = []
    for prefix, status in EXPECTED.items():
        match = [r for name, r in by_name.items() if name.startswith(prefix)]
        if not match:
            problems.append(f"{prefix}: test not found in run_results")
        elif match[0]["status"] != status:
            problems.append(f"{prefix}: expected {status}, got {match[0]['status']}")
    marts = [r for r in results if r["unique_id"].startswith("model.") and ".fct_" in r["unique_id"]]
    if not marts or any(r["status"] != "skipped" for r in marts):
        problems.append("fct_earthquakes was built from corrupted data (expected: skipped)")
    for p in problems:
        print(f"::error::{p}")
    if not problems:
        print("All injected faults were caught; downstream models were skipped.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
