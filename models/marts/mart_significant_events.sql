-- Events of magnitude 4.5 and above (the USGS "significant" feed threshold).
select
    event_id,
    event_at_utc,
    magnitude,
    magnitude_type,
    magnitude_class,
    depth_km,
    depth_class,
    place,
    region,
    country_or_area,
    network_name,
    review_status,
    round(minutes_to_last_update / 60.0, 1) as hours_to_last_update,
    latitude,
    longitude
from {{ ref('fct_earthquakes') }}
where magnitude >= 4.5
order by magnitude desc
