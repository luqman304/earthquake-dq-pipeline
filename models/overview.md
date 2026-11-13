{% docs __overview__ %}

# Earthquake Data-Quality Pipeline

Live documentation and lineage for a dbt + DuckDB pipeline over the
[USGS FDSN Event API](https://earthquake.usgs.gov/fdsnws/event/1/).
This site is rebuilt and published by GitHub Actions on every scheduled run.

**Repository:** [luqman304/earthquake-dq-pipeline](https://github.com/luqman304/earthquake-dq-pipeline)

## Layers

| Layer | Schema | What it holds |
|---|---|---|
| raw | `raw` | Exactly what the API returned, every column as `VARCHAR`, plus `_source_file` and `_loaded_at`. Guarded by 11 tests and a freshness check. |
| reference | `reference` | Seeds: `seismic_networks`, `magnitude_classes`, `region_aliases`. |
| staging | `staging` | `stg_usgs__earthquakes`: typed, renamed, de-duplicated to the latest revision of each event. |
| intermediate | `intermediate` | `int_earthquakes__enriched`: canonical region and country, network name, magnitude and depth classes, radiated energy, revision latency. |
| marts | `marts` | `fct_earthquakes` (enforced contract), `dim_regions`, `mart_daily_seismicity`, `mart_network_operations`, `mart_significant_events`. |
| failures | `dq_failures` | The failing rows of every test (`store_failures: true`). |

## Data quality

38 data tests run on every build: dbt generic tests, singular SQL tests, `dbt_utils` and
`dbt_expectations`, plus source freshness (warn 6 h / error 24 h) and a model contract on
`fct_earthquakes`.

Severity is chosen by impact. Problems that would corrupt analytics (missing keys, impossible
coordinates or magnitudes, future timestamps, broken aggregation grains) are **error** and stop
the build, so no mart is rebuilt from bad data. Things that are expected in a live feed (a new
event type, a new contributing network, duplicates at download boundaries) are **warn**.

Reports from the latest run are published next to this site:
[quality_report.md](quality_report.md) · [analytics_snapshot.md](analytics_snapshot.md) ·
[run_results.json](run_results.json) · [manifest.json](manifest.json) · [catalog.json](catalog.json)

## Lineage

Click the blue graph icon in the bottom-right corner to open the full lineage graph, or open any
model to see its parents, children, columns and tests.

{% enddocs %}
