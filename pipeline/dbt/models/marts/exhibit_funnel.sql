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

step_mapped as (
    select
        visitor_id,
        case step_name
            when 'welcome' then 1
            when 'the-loop' then 2
            when 'stream' then 2
            when 'the-warehouse' then 3
            when 'warehouse' then 3
            when 'the-pipeline' then 4
            when 'analytics' then 4
            when 'modeling' then 5
            when 'the-apparatus' then 5
            when 'the-shop' then 5
            when 'shop' then 5
        end as step_number
    from funnel_events
),

step_names as (
    select 1 as step_number, 'welcome' as step_name union all
    select 2, 'stream' union all
    select 3, 'warehouse' union all
    select 4, 'analytics' union all
    select 5, 'modeling'
),

step_visitors as (
    select
        step_number,
        count(distinct visitor_id) as unique_visitors
    from step_mapped
    where step_number is not null
    group by step_number
),

step1_visitors as (
    select unique_visitors as total
    from step_visitors
    where step_number = 1
)

select
    sn.step_name,
    sv.step_number,
    sv.unique_visitors,
    safe_divide(sv.unique_visitors, s1.total) as completion_rate
from step_visitors sv
join step_names sn on sv.step_number = sn.step_number
cross join step1_visitors s1
order by sv.step_number
