-- Operational SLA: an M4.5+ event older than 48 hours should have been reviewed by a seismologist.
{{ config(severity = 'warn') }}

select event_id, event_at_utc, magnitude, place, review_status
from {{ ref('fct_earthquakes') }}
where magnitude >= 4.5
  and not is_reviewed
  and event_at_utc < (now() at time zone 'UTC') - interval 48 hour
