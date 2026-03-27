-- Questionnaire responses from exhibit visitors.
-- One row per response, extracted from questionnaire_response events.

select
    event_id,
    visitor_id,
    event_timestamp as responded_at,
    json_value(raw_properties, '$.response_text') as response_text

from {{ ref('stg_events') }}
where event_name = 'questionnaire_response'
  and json_value(raw_properties, '$.response_text') is not null
