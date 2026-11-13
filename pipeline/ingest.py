"""Extract earthquake events from the USGS FDSN Event API and load them into DuckDB.

The raw layer is deliberately "dumb": every column is stored as VARCHAR exactly
as the API returned it, plus two lineage columns (_source_file, _loaded_at).
Typing, de-duplication and validation all happen downstream in dbt, so that the
raw table is a faithful record of what the source sent.

Usage:
    python pipeline/ingest.py                      # last 30 days, all magnitudes
    python pipeline/ingest.py --days 14
    python pipeline/ingest.py --inject-faults      # also load corrupted rows (DQ demo)
"""

from __future__ import annotations

import argparse
import csv
import io
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import duckdb
import requests

API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = Path(os.environ.get("DUCKDB_PATH", ROOT / "data" / "warehouse.duckdb"))
RAW_DIR = ROOT / "data" / "raw"
CHUNK_DAYS = 7  # the API caps a single response at 20,000 events
FAULT_FILE = "fault_injection.csv"

log = logging.getLogger("ingest")


def fetch_chunk(start: datetime, end: datetime, min_mag: float | None, retries: int = 4) -> str:
    """Download one time window as CSV text, with simple exponential backoff."""
    params = {
        "format": "csv",
        "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "orderby": "time-asc",
    }
    if min_mag is not None:
        params["minmagnitude"] = min_mag
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(API_URL, params=params, timeout=120)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            if attempt == retries:
                raise
            wait = 2**attempt
            log.warning("attempt %d failed (%s); retrying in %ds", attempt, exc, wait)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def download(days: int, min_mag: float | None, now: datetime) -> list[Path]:
    """Download the window [now - days, now] in weekly chunks to data/raw/."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for old in RAW_DIR.glob("usgs_*.csv"):
        old.unlink()  # each run is a full refresh of the rolling window

    files: list[Path] = []
    start = now - timedelta(days=days)
    while start < now:
        end = min(start + timedelta(days=CHUNK_DAYS), now)
        text = fetch_chunk(start, end, min_mag)
        path = RAW_DIR / f"usgs_{start:%Y%m%dT%H%M}_{end:%Y%m%dT%H%M}.csv"
        path.write_text(text, encoding="utf-8")
        rows = max(text.count("\n") - 1, 0)
        log.info("downloaded %s (%d rows)", path.name, rows)
        files.append(path)
        start = end
    return files


def write_fault_file(template: Path) -> Path:
    """Write a small CSV of deliberately broken events, using real rows as a base.

    Each row breaks one data contract that the dbt source tests enforce, so the
    demo shows exactly which test catches which fault.
    """
    with template.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames
        base = [row for _, row in zip(range(5), reader)]
    if not header or len(base) < 5:
        raise SystemExit("not enough rows to build fault rows from")

    future = (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    faults = [
        {**base[0], "id": "", "place": "FAULT: missing event id"},
        {**base[1], "id": "fault_mag", "mag": "12.4", "place": "FAULT: impossible magnitude"},
        {**base[2], "id": "fault_lat", "latitude": "123.45", "place": "FAULT: latitude out of range"},
        {**base[3], "id": "fault_future", "time": future, "updated": future,
         "place": "FAULT: event time in the future"},
        {**base[4], "id": "fault_type", "type": "alien invasion", "place": "FAULT: unknown event type"},
    ]
    path = RAW_DIR / FAULT_FILE
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        writer.writerows(faults)
    log.warning("wrote %d deliberately corrupted rows to %s", len(faults), path.name)
    return path


def load(db_path: Path, files: list[Path]) -> int:
    """Replace raw.usgs_earthquakes with the contents of the downloaded files."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    try:
        con.execute("create schema if not exists raw")
        file_list = ", ".join(f"'{p.as_posix()}'" for p in files)
        con.execute(
            f"""
            create or replace table raw.usgs_earthquakes as
            select
                * exclude (filename),
                regexp_extract(filename, '[^/]+$') as _source_file,
                current_timestamp::timestamptz      as _loaded_at
            from read_csv([{file_list}], all_varchar = true, header = true,
                          filename = true, union_by_name = true)
            """
        )
        (count,) = con.execute("select count(*) from raw.usgs_earthquakes").fetchone()
        return count
    finally:
        con.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=int(os.environ.get("INGEST_DAYS", 30)),
                        help="size of the rolling window in days (default 30)")
    parser.add_argument("--min-magnitude", type=float, default=None,
                        help="optional magnitude floor to keep the sample small")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="DuckDB file to load into")
    parser.add_argument("--inject-faults", action="store_true",
                        help="add deliberately corrupted rows to demo the quality gates")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    files = download(args.days, args.min_magnitude, now)
    fault = RAW_DIR / FAULT_FILE
    if fault.exists():
        fault.unlink()
    if args.inject_faults:
        files.append(write_fault_file(files[-1]))
    count = load(args.db, files)
    log.info("loaded %d rows into raw.usgs_earthquakes (%s)", count, args.db)
    return 0


if __name__ == "__main__":
    sys.exit(main())
