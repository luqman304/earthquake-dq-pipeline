-- Contract: the source must never report an event whose origin time is in the future.
-- A 5-minute tolerance absorbs clock skew between USGS and the runner.
{{ config(severity = 'error') }}

select id, "time", place
from {{ source('usgs', 'earthquakes') }}
where try_cast("time" as timestamp) > (now() at time zone 'UTC') + interval 5 minute
