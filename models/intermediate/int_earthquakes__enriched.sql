-- Adds reference data and derived attributes to every event:
-- canonical region, network name, magnitude class, depth class, energy and review latency.
with events as (

    select * from {{ ref('stg_usgs__earthquakes') }}

),

aliases as (

    select * from {{ ref('region_aliases') }}

),

networks as (

    select * from {{ ref('seismic_networks') }}

),

classes as (

    select * from {{ ref('magnitude_classes') }}

),

regions as (

    select
        events.*,
        -- "Japan region" and "Japan" describe the same area
        regexp_replace(events.region_raw, '\s+region$', '') as region_stripped
    from events

),

normalised as (

    select
        regions.*,
        case
            -- USGS writes "Georgia" for both the US state and the country
            when regions.region_stripped = 'Georgia' and regions.longitude > 0 then 'Georgia (country)'
            else coalesce(aliases.canonical_region, regions.region_stripped)
        end as region,
        case
            when regions.region_stripped = 'Georgia' and regions.longitude > 0 then 'Georgia'
            else coalesce(aliases.country, regions.region_stripped)
        end as country_or_area,
        aliases.raw_region is not null and aliases.raw_region <> aliases.canonical_region
            as region_was_aliased
    from regions
    left join aliases
        on regions.region_stripped = aliases.raw_region

)

select
    normalised.event_id,
    normalised.event_at_utc,
    cast(normalised.event_at_utc as date)                       as event_date,
    normalised.updated_at_utc,
    normalised.latitude,
    normalised.longitude,
    normalised.depth_km,
    case
        when normalised.depth_km < 70  then 'shallow'
        when normalised.depth_km < 300 then 'intermediate'
        else 'deep'
    end                                                         as depth_class,
    normalised.magnitude,
    normalised.magnitude_type,
    coalesce(classes.magnitude_class, 'unknown')                as magnitude_class,
    -- Gutenberg-Richter energy relation, log10(E) = 1.5 M + 4.8 (joules)
    power(10, 1.5 * normalised.magnitude + 4.8)                 as energy_joules,
    normalised.event_type,
    normalised.event_type = 'earthquake'                        as is_tectonic,
    normalised.place,
    normalised.region_raw,
    normalised.region,
    normalised.country_or_area,
    normalised.region_was_aliased,
    normalised.network_code,
    coalesce(networks.network_name, 'Unknown network')         as network_name,
    normalised.review_status,
    normalised.review_status = 'reviewed'                       as is_reviewed,
    date_diff('minute', normalised.event_at_utc, normalised.updated_at_utc)
                                                                as minutes_to_last_update,
    normalised.station_count,
    normalised.azimuthal_gap_deg,
    normalised.horizontal_error_km,
    normalised.depth_error_km,
    normalised.magnitude_error,
    normalised._source_file,
    normalised._loaded_at
from normalised
left join networks
    on normalised.network_code = networks.network_code
left join classes
    on normalised.magnitude >= classes.min_magnitude
   and normalised.magnitude <  classes.max_magnitude
