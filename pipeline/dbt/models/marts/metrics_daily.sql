-- Daily aggregate metrics for the analytics page.
-- One row per day. Powers the site's self-referential dashboards.

with events as (
    select * from {{ ref('fct_events') }}
),

purchases as (
    select * from {{ ref('fct_purchases') }}
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

        -- Device mix (distinct sessions per device type)
        count(distinct case when device_type = 'Desktop' then session_id end) as desktop_sessions,
        count(distinct case when device_type = 'Mobile' then session_id end) as mobile_sessions,
        count(distinct case when device_type = 'Tablet' then session_id end) as tablet_sessions,

        -- Geo
        count(distinct country) as distinct_countries

    from events
    where event_timestamp is not null
    group by metric_date
),

daily_purchases as (
    select
        date(purchased_at) as metric_date,
        count(*) as total_purchases,
        coalesce(sum(price), 0) as total_revenue
    from purchases
    group by metric_date
)

select
    d.metric_date,
    d.total_events,
    d.unique_visitors,
    d.unique_sessions,
    d.pageviews,
    d.clicks,
    d.custom_events,
    d.distinct_pages_viewed,
    d.desktop_sessions,
    d.mobile_sessions,
    d.tablet_sessions,
    d.distinct_countries,

    -- Purchases
    coalesce(p.total_purchases, 0) as total_purchases,
    coalesce(p.total_revenue, 0) as total_revenue,

    -- Derived ratios
    safe_divide(d.total_events, d.unique_visitors) as events_per_visitor,
    safe_divide(d.pageviews, d.unique_sessions) as pages_per_session,
    safe_divide(d.clicks, d.pageviews) as click_through_rate

from daily d
left join daily_purchases p on d.metric_date = p.metric_date
order by d.metric_date desc
