-- Core event fact table.
-- Currently a clean pass-through from staging.
-- Business logic (event categorization, enrichment) gets added here.

select
    event_id,
    event_name,
    visitor_id,
    session_id,
    event_timestamp,
    current_url,
    page_path,
    referrer,
    browser,
    os,
    device_type,
    country,
    city,
    element_text,
    ip
from {{ ref('stg_events') }}
