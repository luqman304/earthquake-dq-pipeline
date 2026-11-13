## Fault-injection run

Generated 2026-11-13 09:29:33 UTC by dbt 1.12.7. **6 pass**, **1 warn**, **4 fail**, **27 skip**

| Status | Severity | Layer | Check | Target | Failing rows |
|---|---|---|---|---|---|
| FAIL | error | raw (source) | `singular: assert_no_future_events_in_source` | `earthquakes` | 1 |
| FAIL | error | raw (source) | `not_null` | `earthquakes.id` | 1 |
| FAIL | error | raw (source) | `text_numeric_in_range` | `earthquakes.latitude` | 1 |
| FAIL | error | raw (source) | `text_numeric_in_range` | `earthquakes.mag` | 1 |
| WARN | warn | raw (source) | `accepted_values` | `earthquakes.type` | 1 |
| SKIP | error | intermediate | `accepted_values` | `int_earthquakes__enriched.depth_class` |  |
| SKIP | error | intermediate | `not_null` | `int_earthquakes__enriched.event_id` |  |
| SKIP | error | intermediate | `unique` | `int_earthquakes__enriched.event_id` |  |
| SKIP | error | intermediate | `accepted_values` | `int_earthquakes__enriched.magnitude_class` |  |
| SKIP | error | intermediate | `dbt_utils.accepted_range` | `int_earthquakes__enriched.minutes_to_last_update` |  |
| SKIP | error | intermediate | `not_null` | `int_earthquakes__enriched.region` |  |
| SKIP | error | marts | `not_null` | `dim_regions.region` |  |
| SKIP | error | marts | `unique` | `dim_regions.region` |  |
| SKIP | warn | marts | `singular: assert_region_abbreviations_resolved` | `fct_earthquakes` |  |
| SKIP | warn | marts | `singular: assert_significant_events_reviewed_within_48h` | `fct_earthquakes` |  |
| SKIP | warn | marts | `dbt_utils.recency` | `fct_earthquakes` |  |
| SKIP | error | marts | `singular: assert_daily_mart_reconciles_with_fact` | `fct_earthquakes, mart_daily_seismicity` |  |
| SKIP | error | marts | `unique` | `fct_earthquakes.event_id` |  |
| SKIP | error | marts | `not_null` | `fct_earthquakes.region` |  |
| SKIP | error | marts | `dbt_utils.unique_combination_of_columns` | `mart_daily_seismicity` |  |
| SKIP | error | marts | `dbt_utils.accepted_range` | `mart_daily_seismicity.event_count` |  |
| SKIP | error | marts | `unique` | `mart_network_operations.network_code` |  |
| SKIP | error | marts | `dbt_utils.accepted_range` | `mart_network_operations.pct_reviewed` |  |
| SKIP | error | marts | `unique` | `mart_significant_events.event_id` |  |
| SKIP | error | marts | `dbt_utils.accepted_range` | `mart_significant_events.magnitude` |  |
| SKIP | error | staging | `dbt_utils.expression_is_true` | `stg_usgs__earthquakes` |  |
| SKIP | error | staging | `dbt_utils.accepted_range` | `stg_usgs__earthquakes.depth_km` |  |
| SKIP | error | staging | `not_null` | `stg_usgs__earthquakes.event_at_utc` |  |
| SKIP | error | staging | `not_null` | `stg_usgs__earthquakes.event_id` |  |
| SKIP | error | staging | `unique` | `stg_usgs__earthquakes.event_id` |  |
| SKIP | warn | staging | `not_null` | `stg_usgs__earthquakes.magnitude` |  |
| SKIP | warn | staging | `relationships` | `stg_usgs__earthquakes.network_code` |  |
| PASS | error | raw (source) | `dbt_expectations.expect_table_row_count_to_be_between` | `earthquakes` | 0 |
| PASS | warn | raw (source) | `unique` | `earthquakes.id` | 0 |
| PASS | error | raw (source) | `text_numeric_in_range` | `earthquakes.longitude` | 0 |
| PASS | error | raw (source) | `dbt_expectations.expect_column_values_to_match_regex` | `earthquakes.net` | 0 |
| PASS | error | raw (source) | `accepted_values` | `earthquakes.status` | 0 |
| PASS | error | raw (source) | `not_null` | `earthquakes.time` | 0 |
