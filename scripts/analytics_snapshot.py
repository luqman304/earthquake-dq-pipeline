"""Print Markdown tables of the headline numbers in the marts (used for the README
and appended to the scheduled run's job summary)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import duckdb

DB = Path(os.environ.get("DUCKDB_PATH", "data/warehouse.duckdb"))

QUERIES = {
    "Window overview": """
        select count(*) as events,
               count(*) filter (where is_tectonic) as earthquakes,
               count(*) filter (where magnitude >= 4.5) as "M4.5+",
               max(magnitude) as max_magnitude,
               strftime(min(event_at_utc), '%Y-%m-%d') as first_day,
               strftime(max(event_at_utc), '%Y-%m-%d %H:%M') as last_event_utc,
               round(avg(is_reviewed::int) * 100, 1) as pct_reviewed
        from marts.fct_earthquakes""",
    "Most events vs most energy (top 6 regions each)": """
        with r as (
            select region, event_count,
                   round(100 * event_count / sum(event_count) over (), 1) as pct_events,
                   round(100 * total_energy_joules / sum(total_energy_joules) over (), 1) as pct_energy,
                   max_magnitude
            from marts.dim_regions)
        (select 'by count' as ranking, * from r order by event_count desc limit 6)
        union all
        (select 'by energy', * from r order by pct_energy desc limit 6)""",
    "Largest events": """
        select strftime(event_at_utc, '%Y-%m-%d %H:%M') as utc, magnitude, magnitude_type as type,
               depth_km, place
        from marts.mart_significant_events order by magnitude desc limit 6""",
    "Seismic network operations": """
        select network_code as net, network_name, event_count as events, pct_reviewed,
               median_hours_to_last_update, p90_hours_to_last_update
        from marts.mart_network_operations order by event_count desc""",
}


def to_markdown(con: duckdb.DuckDBPyConnection, sql: str) -> str:
    rel = con.sql(sql)
    cols = rel.columns
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in rel.fetchall():
        out.append("| " + " | ".join("" if v is None else str(v) for v in row) + " |")
    return "\n".join(out)


def main() -> None:
    con = duckdb.connect(str(DB), read_only=True)
    parts = []
    for title, sql in QUERIES.items():
        parts.append(f"### {title}\n\n{to_markdown(con, sql)}\n")
    text = "\n".join(parts)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
