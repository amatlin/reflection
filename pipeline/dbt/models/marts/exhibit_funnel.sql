-- Exhibit step completion funnel.
-- One row per step with unique visitors and completion rate.
-- Reads from stg_events to access raw_properties for the step name.

with funnel_events as (
    select
        visitor_id,
        json_value(raw_properties, '$.step') as step_name
    from {{ ref('stg_events') }}
    where event_name = 'funnel_step'
      and json_value(raw_properties, '$.step') is not null
),

step_visitors as (
    select
        step_name,
        case step_name
            when 'welcome' then 1
            when 'the-loop' then 2
            when 'stream' then 2
            when 'the-warehouse' then 3
            when 'warehouse' then 3
            when 'the-pipeline' then 4
            when 'analytics' then 4
            when 'the-apparatus' then 5
            when 'the-shop' then 5
            when 'shop' then 5
        end as step_number,
        count(distinct visitor_id) as unique_visitors
    from funnel_events
    group by step_name
),

step1_visitors as (
    select unique_visitors as total
    from step_visitors
    where step_number = 1
)

select
    sv.step_name,
    sv.step_number,
    sv.unique_visitors,
    safe_divide(sv.unique_visitors, s1.total) as completion_rate
from step_visitors sv
cross join step1_visitors s1
where sv.step_number is not null
order by sv.step_number
