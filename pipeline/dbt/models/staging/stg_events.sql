-- Staging layer: clean and type the raw PostHog export.
-- Extracts commonly-used properties into real columns.
-- Deduplicated by event UUID.

with source as (
    select * from `reflection-data.reflection.posthog_events`
),

deduplicated as (
    select
        *,
        row_number() over (partition by uuid order by bq_ingested_timestamp desc) as _row_num
    from source
)

select
    uuid as event_id,
    event as event_name,
    distinct_id as visitor_id,
    timestamp as event_timestamp,
    bq_ingested_timestamp,

    -- Page info
    json_value(properties, '$.$current_url') as current_url,
    json_value(properties, '$.$pathname') as page_path,
    json_value(properties, '$.$host') as page_host,
    json_value(properties, '$.$referrer') as referrer,

    -- Device / browser
    json_value(properties, '$.$browser') as browser,
    json_value(properties, '$.$browser_version') as browser_version,
    json_value(properties, '$.$os') as os,
    json_value(properties, '$.$device_type') as device_type,
    json_value(properties, '$.$screen_height') as screen_height,
    json_value(properties, '$.$screen_width') as screen_width,

    -- Geo
    json_value(properties, '$.$geoip_country_name') as country,
    json_value(properties, '$.$geoip_city_name') as city,
    json_value(properties, '$.$geoip_time_zone') as timezone,

    -- Session
    json_value(properties, '$.$session_id') as session_id,

    -- Element info (for autocapture clicks)
    json_value(properties, '$.$el_text') as element_text,

    -- Full properties for anything not extracted above
    properties as raw_properties,

    ip

from deduplicated
where _row_num = 1
