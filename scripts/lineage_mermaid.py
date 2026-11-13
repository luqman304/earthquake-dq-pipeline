"""Generate a Mermaid lineage diagram from dbt's manifest.json.

The diagram in the README is produced by this script, so it always matches the
real DAG rather than a hand-drawn approximation.

Usage: python scripts/lineage_mermaid.py [--manifest target/manifest.json] [--tests]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

STYLE = {
    "api": "fill:#fff,stroke:#b45309,stroke-dasharray:4,color:#111",
    "source": "fill:#fde68a,stroke:#b45309,color:#111",
    "seed": "fill:#e5e7eb,stroke:#4b5563,color:#111",
    "staging": "fill:#bfdbfe,stroke:#1d4ed8,color:#111",
    "intermediate": "fill:#c7d2fe,stroke:#4338ca,color:#111",
    "marts": "fill:#bbf7d0,stroke:#15803d,color:#111",
}


def node_id(uid: str) -> str:
    return uid.replace(".", "_")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="target/manifest.json")
    ap.add_argument("--tests", action="store_true", help="annotate each node with its test count")
    args = ap.parse_args()
    m = json.loads(Path(args.manifest).read_text())

    tests = Counter()
    for n in m["nodes"].values():
        if n["resource_type"] == "test":
            for d in n.get("depends_on", {}).get("nodes", []):
                if not d.startswith("seed."):
                    tests[d] += 1

    lines = ["flowchart LR", '    api(["USGS FDSN Event API"]) -->|"pipeline/ingest.py"| SRC']
    classes: dict[str, list[str]] = {k: [] for k in STYLE}
    classes["api"].append("api")
    edges = []
    for uid, s in m["sources"].items():
        label = f"raw.{s['identifier']}"
        if args.tests and tests[uid]:
            label += f"<br/>{tests[uid]} tests + freshness"
        lines.append(f'    {node_id(uid)}[("{label}")]')
        lines[1] = lines[1].replace("SRC", node_id(uid))
        classes["source"].append(node_id(uid))
    for uid, n in m["nodes"].items():
        if n["resource_type"] not in {"model", "seed"} or n["package_name"] != m["metadata"].get("project_name", n["package_name"]):
            continue
        label = n["name"]
        if args.tests and tests[uid]:
            label += f"<br/>{tests[uid]} tests"
        if n["resource_type"] == "seed":
            lines.append(f'    {node_id(uid)}[/"{label}"/]')
            classes["seed"].append(node_id(uid))
        else:
            layer = n["fqn"][1] if len(n["fqn"]) > 2 else "marts"
            lines.append(f'    {node_id(uid)}["{label}"]')
            classes.setdefault(layer, []).append(node_id(uid))
        for dep in n.get("depends_on", {}).get("nodes", []):
            if dep.split(".")[0] in {"model", "seed", "source"}:
                edges.append(f"    {node_id(dep)} --> {node_id(uid)}")
    lines += sorted(set(edges))
    for cls, ids in classes.items():
        if ids:
            lines.append(f"    classDef {cls} {STYLE.get(cls, '')}")
            lines.append(f"    class {','.join(ids)} {cls}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
