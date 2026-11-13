-- Reconciliation: rolling the daily mart back up must give exactly the fact table's row count.
{{ config(severity = 'error') }}

with mart as (
    select sum(event_count) as n from {{ ref('mart_daily_seismicity') }}
),
fact as (
    select count(*) as n from {{ ref('fct_earthquakes') }}
)
select mart.n as mart_events, fact.n as fact_events
from mart, fact
where mart.n <> fact.n
