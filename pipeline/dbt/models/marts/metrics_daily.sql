-- Daily aggregate metrics for the analytics page.
-- One row per day. Powers the site's self-referential dashboards.

with events as (
    select * from {{ ref('fct_events') }}
),

daily as (
    select
        date(event_timestamp) as metric_date,

        -- Volume
        count(*) as total_events,
        count(distinct visitor_id) as unique_visitors,
        count(distinct session_id) as unique_sessions,

        -- Event mix
        countif(event_name = '$pageview') as pageviews,
        countif(event_name = '$autocapture') as clicks,
        countif(event_name not in ('$pageview', '$autocapture')) as custom_events,

        -- Depth
        count(distinct page_path) as distinct_pages_viewed,

        -- Device mix
        countif(device_type = 'Desktop') as desktop_sessions,
        countif(device_type = 'Mobile') as mobile_sessions,
        countif(device_type = 'Tablet') as tablet_sessions,

        -- Geo
        count(distinct country) as distinct_countries

    from events
    where event_timestamp is not null
    group by metric_date
)

select
    metric_date,
    total_events,
    unique_visitors,
    unique_sessions,
    pageviews,
    clicks,
    custom_events,
    distinct_pages_viewed,
    desktop_sessions,
    mobile_sessions,
    tablet_sessions,
    distinct_countries,

    -- Derived ratios
    safe_divide(total_events, unique_visitors) as events_per_visitor,
    safe_divide(pageviews, unique_sessions) as pages_per_session,
    safe_divide(clicks, pageviews) as click_through_rate

from daily
order by metric_date desc
