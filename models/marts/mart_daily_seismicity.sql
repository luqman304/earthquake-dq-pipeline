-- Daily activity per region: the grain dashboards and alerts are built on.
select
    event_date,
    region,
    count(*)                                                as event_count,
    count(*) filter (where is_tectonic)                     as earthquake_count,
    count(*) filter (where not is_tectonic)                 as non_tectonic_count,
    count(*) filter (where magnitude >= 2.5)                as m25_plus_count,
    max(magnitude)                                          as max_magnitude,
    round(avg(depth_km), 1)                                 as avg_depth_km,
    sum(energy_joules)                                      as total_energy_joules
from {{ ref('fct_earthquakes') }}
group by 1, 2
