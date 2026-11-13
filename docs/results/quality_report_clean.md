## Clean run

Generated 2026-11-13 09:30:24 UTC by dbt 1.12.7. **38 pass**

| Status | Severity | Layer | Check | Target | Failing rows |
|---|---|---|---|---|---|
| PASS | error | intermediate | `accepted_values` | `int_earthquakes__enriched.depth_class` | 0 |
| PASS | error | intermediate | `not_null` | `int_earthquakes__enriched.event_id` | 0 |
| PASS | error | intermediate | `unique` | `int_earthquakes__enriched.event_id` | 0 |
| PASS | error | intermediate | `accepted_values` | `int_earthquakes__enriched.magnitude_class` | 0 |
| PASS | error | intermediate | `dbt_utils.accepted_range` | `int_earthquakes__enriched.minutes_to_last_update` | 0 |
| PASS | error | intermediate | `not_null` | `int_earthquakes__enriched.region` | 0 |
| PASS | error | marts | `unique` | `dim_regions.region` | 0 |
| PASS | error | marts | `not_null` | `dim_regions.region` | 0 |
| PASS | warn | marts | `singular: assert_region_abbreviations_resolved` | `fct_earthquakes` | 0 |
| PASS | warn | marts | `dbt_utils.recency` | `fct_earthquakes` | 0 |
| PASS | warn | marts | `singular: assert_significant_events_reviewed_within_48h` | `fct_earthquakes` | 0 |
| PASS | error | marts | `singular: assert_daily_mart_reconciles_with_fact` | `fct_earthquakes, mart_daily_seismicity` | 0 |
| PASS | error | marts | `unique` | `fct_earthquakes.event_id` | 0 |
| PASS | error | marts | `not_null` | `fct_earthquakes.region` | 0 |
| PASS | error | marts | `dbt_utils.unique_combination_of_columns` | `mart_daily_seismicity` | 0 |
| PASS | error | marts | `dbt_utils.accepted_range` | `mart_daily_seismicity.event_count` | 0 |
| PASS | error | marts | `unique` | `mart_network_operations.network_code` | 0 |
| PASS | error | marts | `dbt_utils.accepted_range` | `mart_network_operations.pct_reviewed` | 0 |
| PASS | error | marts | `unique` | `mart_significant_events.event_id` | 0 |
| PASS | error | marts | `dbt_utils.accepted_range` | `mart_significant_events.magnitude` | 0 |
| PASS | error | raw (source) | `singular: assert_no_future_events_in_source` | `earthquakes` | 0 |
| PASS | error | raw (source) | `dbt_expectations.expect_table_row_count_to_be_between` | `earthquakes` | 0 |
| PASS | error | raw (source) | `not_null` | `earthquakes.id` | 0 |
| PASS | warn | raw (source) | `unique` | `earthquakes.id` | 0 |
| PASS | error | raw (source) | `text_numeric_in_range` | `earthquakes.latitude` | 0 |
| PASS | error | raw (source) | `text_numeric_in_range` | `earthquakes.longitude` | 0 |
| PASS | error | raw (source) | `text_numeric_in_range` | `earthquakes.mag` | 0 |
| PASS | error | raw (source) | `dbt_expectations.expect_column_values_to_match_regex` | `earthquakes.net` | 0 |
| PASS | error | raw (source) | `accepted_values` | `earthquakes.status` | 0 |
| PASS | error | raw (source) | `not_null` | `earthquakes.time` | 0 |
| PASS | warn | raw (source) | `accepted_values` | `earthquakes.type` | 0 |
| PASS | error | staging | `dbt_utils.expression_is_true` | `stg_usgs__earthquakes` | 0 |
| PASS | error | staging | `dbt_utils.accepted_range` | `stg_usgs__earthquakes.depth_km` | 0 |
| PASS | error | staging | `not_null` | `stg_usgs__earthquakes.event_at_utc` | 0 |
| PASS | error | staging | `not_null` | `stg_usgs__earthquakes.event_id` | 0 |
| PASS | error | staging | `unique` | `stg_usgs__earthquakes.event_id` | 0 |
| PASS | warn | staging | `not_null` | `stg_usgs__earthquakes.magnitude` | 0 |
| PASS | warn | staging | `relationships` | `stg_usgs__earthquakes.network_code` | 0 |
