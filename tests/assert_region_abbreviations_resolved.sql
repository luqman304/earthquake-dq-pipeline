-- Real-world issue in the USGS feed: the same region appears under several names
-- ("CA" and "California", "MX" and "Mexico", "Japan region" and "Japan").
-- The region_aliases seed normalises the known ones. This test warns when a new
-- short code turns up that the seed does not cover yet.
{{ config(severity = 'warn') }}

select region, count(*) as events
from {{ ref('fct_earthquakes') }}
where regexp_full_match(region, '[A-Z][A-Z.]{1,3}')
group by 1
