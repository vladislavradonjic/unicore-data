{{ config(materialized='table') }}

-- Asset card (Kartica OS) — chronological event history per asset.
-- Union of four event types: ACTIVATION, DISPOSAL, LOCATION_CHANGE, DEPRECIATION.
-- No output ports — consumers query directly with WHERE asset_id = :id.

with assets as (

    select asset_id, asset_number, asset_type, category_code, asset_name
    from {{ ref('ASST_t1_T') }}

),

-- 1. Activation events
activation_events as (

    select
        req.asset_id,
        'ACTIVATION'                    as event_type,
        req.requested_effective_date    as event_date,
        req.request_number              as reference_number,
        req.created_by                  as actor,
        cast(null as varchar)           as from_value,
        cast(null as varchar)           as to_value,
        cast(null as varchar)           as note,
        req.business_ts
    from {{ ref('ASOP_t1_T') }} req
    where req.operation_type = 'ACTIVATION'

),

-- 2. Disposal events
disposal_events as (

    select
        req.asset_id,
        'DISPOSAL'                      as event_type,
        req.requested_effective_date    as event_date,
        req.request_number              as reference_number,
        req.created_by                  as actor,
        cast(null as varchar)           as from_value,
        cast(null as varchar)           as to_value,
        cast(null as varchar)           as note,
        req.business_ts
    from {{ ref('ASOP_t1_T') }} req
    where req.operation_type = 'DISPOSAL'

),

-- 3. Location/custodian changes (every assignment after the first)
assignment_events as (

    select
        m.asset_id,
        m.movement_type                 as event_type,
        m.effective_from                as event_date,
        m.assignment_id                 as reference_number,
        cast(null as varchar)           as actor,
        m.prev_location_code            as from_value,
        m.location_code                 as to_value,
        cast(null as varchar)           as note,
        m.business_ts
    from {{ ref('MOVE_T') }} m
    where m.movement_type != 'INITIAL_ASSIGNMENT'

),

-- 4. Depreciation events (one per completed period)
depreciation_events as (

    select
        d.asset_id,
        'DEPRECIATION'                  as event_type,
        d.period_starts_on              as event_date,
        d.run_number                    as reference_number,
        d.initiated_by                  as actor,
        cast(null as varchar)           as from_value,
        cast(d.depreciation_amount as varchar) as to_value,
        d.period_code                   as note,
        d.business_ts
    from {{ ref('AMRT_T') }} d

),

all_events as (

    select * from activation_events
    union all
    select * from disposal_events
    union all
    select * from assignment_events
    union all
    select * from depreciation_events

),

final as (

    select
        e.asset_id,
        a.asset_number,
        a.asset_type,
        a.category_code,
        a.asset_name,
        e.event_type,
        e.event_date,
        e.reference_number,
        e.actor,
        e.from_value,
        e.to_value,
        e.note,
        e.business_ts,
        current_timestamp   as technical_ts
    from all_events e
    left join assets a on a.asset_id = e.asset_id
    where e.asset_id is not null

)

select * from final
order by asset_id, event_date, event_type
