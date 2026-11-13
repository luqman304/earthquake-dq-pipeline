-- How each contributing seismic network performs: volume, review coverage and revision latency
-- (hours from origin time to the latest update of reviewed events).
select
    network_code,
    network_name,
    count(*)                                                        as event_count,
    round(avg(is_reviewed::int) * 100, 1)                           as pct_reviewed,
    round(median(minutes_to_last_update) filter (where is_reviewed) / 60.0, 1)
                                                                    as median_hours_to_last_update,
    round(quantile_cont(minutes_to_last_update, 0.9) filter (where is_reviewed) / 60.0, 1)
                                                                    as p90_hours_to_last_update,
    round(avg(station_count), 1)                                    as avg_station_count,
    round(avg(horizontal_error_km), 2)                              as avg_horizontal_error_km,
    min(magnitude)                                                  as min_magnitude,
    max(magnitude)                                                  as max_magnitude
from {{ ref('fct_earthquakes') }}
group by 1, 2
