-- One row per canonical region with activity totals for the window.
select
    region,
    country_or_area,
    country_or_area = 'United States'                       as is_united_states,
    count(*)                                                as event_count,
    count(*) filter (where is_tectonic)                     as earthquake_count,
    count(*) filter (where magnitude >= 2.5)                as m25_plus_count,
    max(magnitude)                                          as max_magnitude,
    round(avg(depth_km), 1)                                 as avg_depth_km,
    sum(energy_joules)                                      as total_energy_joules,
    min(event_at_utc)                                       as first_event_at_utc,
    max(event_at_utc)                                       as last_event_at_utc,
    bool_or(region_was_aliased)                             as had_aliased_names
from {{ ref('int_earthquakes__enriched') }}
group by 1, 2
