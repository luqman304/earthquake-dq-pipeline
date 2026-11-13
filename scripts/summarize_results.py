"""Turn dbt's run_results.json + manifest.json into a Markdown data-quality report.

Used in three places:
  * locally, to produce docs/quality_report_*.md for the README
  * in GitHub Actions, appended to $GITHUB_STEP_SUMMARY
  * in the Pages site, as quality.md next to the dbt docs

Usage:
    python scripts/summarize_results.py [--target target] [--title "..."] [--out report.md]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ICON = {"pass": "PASS", "warn": "WARN", "fail": "FAIL", "error": "ERROR", "skipped": "SKIP"}
ORDER = {"error": 0, "fail": 1, "warn": 2, "skipped": 3, "pass": 4}


def layer_of(node: dict) -> str:
    deps = node.get("depends_on", {}).get("nodes", [])
    if any(d.startswith("source.") for d in deps):
        return "raw (source)"
    for d in deps:
        name = d.split(".")[-1]
        if name.startswith("stg_"):
            return "staging"
        if name.startswith("int_"):
            return "intermediate"
    return "marts"


def describe(node: dict) -> tuple[str, str]:
    """Return (test type, target column/model) in readable form."""
    meta = node.get("test_metadata") or {}
    if meta:
        ns = meta.get("namespace")
        kind = f"{ns}.{meta['name']}" if ns else meta["name"]
    else:
        kind = "singular: " + node["name"]
    deps = [d.split(".")[-1] for d in node.get("depends_on", {}).get("nodes", [])]
    deps = [d for d in deps if d not in {"seismic_networks", "region_aliases", "magnitude_classes"}] or deps
    target = ", ".join(sorted(set(deps)))
    col = node.get("column_name")
    if col:
        target += f".{col}"
    return kind, target


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="target")
    ap.add_argument("--title", default="Data-quality report")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    target = Path(args.target)
    results = json.loads((target / "run_results.json").read_text())
    manifest = json.loads((target / "manifest.json").read_text())
    nodes = manifest["nodes"]

    rows = []
    for r in results["results"]:
        node = nodes.get(r["unique_id"])
        if not node or node["resource_type"] != "test":
            continue
        kind, tgt = describe(node)
        rows.append({
            "status": r["status"],
            "severity": node["config"].get("severity", "error").lower(),
            "layer": layer_of(node),
            "kind": kind,
            "target": tgt,
            "failures": r.get("failures"),
        })
    rows.sort(key=lambda x: (ORDER.get(x["status"], 9), x["layer"], x["target"]))

    counts = Counter(r["status"] for r in rows)
    gen = results["metadata"]["generated_at"][:19].replace("T", " ")
    lines = [
        f"## {args.title}",
        "",
        f"Generated {gen} UTC by dbt {results['metadata']['dbt_version']}. "
        + ", ".join(f"**{counts.get(s, 0)} {ICON[s].lower()}**" for s in ["pass", "warn", "fail", "error", "skipped"]
                    if counts.get(s)),
        "",
        "| Status | Severity | Layer | Check | Target | Failing rows |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        failures = "" if r["failures"] is None else str(r["failures"])
        lines.append(f"| {ICON.get(r['status'], r['status'])} | {r['severity']} | {r['layer']} | "
                     f"`{r['kind']}` | `{r['target']}` | {failures} |")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
