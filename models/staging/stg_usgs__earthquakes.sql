-- Typed, renamed and de-duplicated USGS events. One row per event_id.
with source as (

    select * from {{ source('usgs', 'earthquakes') }}

),

typed as (

    select
        id                                         as event_id,
        try_cast("time" as timestamp)              as event_at_utc,
        try_cast(updated as timestamp)             as updated_at_utc,
        try_cast(latitude as double)               as latitude,
        try_cast(longitude as double)              as longitude,
        try_cast(depth as double)                  as depth_km,
        try_cast(mag as double)                    as magnitude,
        lower(magType)                             as magnitude_type,
        try_cast(nst as integer)                   as station_count,
        try_cast(gap as double)                    as azimuthal_gap_deg,
        try_cast(dmin as double)                   as nearest_station_deg,
        try_cast(rms as double)                    as rms_residual_s,
        lower(net)                                 as network_code,
        place,
        -- "8 km W of Cobb, CA" -> "CA"; "Fiji region" -> "Fiji region"
        trim(case when place like '%, %'
                  then regexp_extract(place, ',\s*([^,]+)$', 1)
                  else place end)                  as region_raw,
        lower("type")                              as event_type,
        try_cast(horizontalError as double)        as horizontal_error_km,
        try_cast(depthError as double)             as depth_error_km,
        try_cast(magError as double)               as magnitude_error,
        try_cast(magNst as integer)                as magnitude_station_count,
        status                                     as review_status,
        lower(locationSource)                      as location_source,
        lower(magSource)                           as magnitude_source,
        _source_file,
        _loaded_at
    from source

),

deduped as (

    select *
    from typed
    where event_id is not null
    -- keep the most recently updated version of each event
    qualify row_number() over (partition by event_id order by updated_at_utc desc nulls last) = 1

)

select * from deduped
