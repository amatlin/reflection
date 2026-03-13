-- Visitor dimension: one row per distinct visitor.
-- Uses most recent event for device/geo attributes.

with visitor_stats as (
    select
        visitor_id,
        min(event_timestamp) as first_seen_at,
        max(event_timestamp) as last_seen_at,
        count(*) as total_events,
        count(distinct session_id) as total_sessions,
        count(distinct date(event_timestamp)) as active_days
    from {{ ref('stg_events') }}
    where visitor_id is not null
    group by visitor_id
),

-- Get device/geo from most recent event
latest_event as (
    select
        visitor_id,
        browser,
        os,
        device_type,
        country,
        city,
        row_number() over (partition by visitor_id order by event_timestamp desc) as _row_num
    from {{ ref('stg_events') }}
    where visitor_id is not null
)

select
    s.visitor_id,
    s.first_seen_at,
    s.last_seen_at,
    s.total_events,
    s.total_sessions,
    s.active_days,
    e.browser,
    e.os,
    e.device_type,
    e.country,
    e.city
from visitor_stats s
left join latest_event e
    on s.visitor_id = e.visitor_id
    and e._row_num = 1
