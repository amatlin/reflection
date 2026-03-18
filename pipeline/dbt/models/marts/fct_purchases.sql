-- Purchase fact table.
-- One row per completed purchase, extracted from purchase_complete events.

select
    event_id,
    visitor_id,
    event_timestamp as purchased_at,

    json_value(raw_properties, '$.item_id') as item_id,
    json_value(raw_properties, '$.item_name') as item_name,
    cast(json_value(raw_properties, '$.price') as float64) as price,
    json_value(raw_properties, '$.stripe_session_id') as stripe_session_id

from {{ ref('stg_events') }}
where event_name = 'purchase_complete'
