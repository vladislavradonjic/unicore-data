{{ config(materialized='table') }}

-- Asset movement history (Kretanje OS) — each assignment record represents
-- a location/custodian state. LAG() provides the previous state so consumers
-- can see what changed. The first assignment per asset has NULL prev_* columns.

with assignments as (

    select * from {{ ref('ASGN_t1_T') }}

),

assets as (

    select asset_id, asset_number, asset_type, category_code, asset_name
    from {{ ref('ASST_t1_T') }}

),

with_lag as (

    select
        asgn.assignment_id,
        asgn.asset_id,
        asgn.organization_unit_code,
        asgn.cost_center_code,
        asgn.location_code,
        asgn.accountable_person_id,
        asgn.accountable_person_name,
        asgn.effective_from,
        asgn.effective_to,
        -- previous state via LAG
        lag(asgn.location_code) over (
            partition by asgn.asset_id order by asgn.effective_from
        )                           as prev_location_code,
        lag(asgn.cost_center_code) over (
            partition by asgn.asset_id order by asgn.effective_from
        )                           as prev_cost_center_code,
        lag(asgn.organization_unit_code) over (
            partition by asgn.asset_id order by asgn.effective_from
        )                           as prev_organization_unit_code,
        lag(asgn.accountable_person_id) over (
            partition by asgn.asset_id order by asgn.effective_from
        )                           as prev_accountable_person_id,
        lag(asgn.accountable_person_name) over (
            partition by asgn.asset_id order by asgn.effective_from
        )                           as prev_accountable_person_name,
        asgn.business_ts,
        asgn.technical_ts
    from assignments asgn

),

final as (

    select
        m.assignment_id,
        m.asset_id,
        a.asset_number,
        a.asset_type,
        a.category_code,
        a.asset_name,
        -- current state
        m.organization_unit_code,
        m.cost_center_code,
        cc.cost_center_name,
        m.location_code,
        loc.location_name,
        loc.city                    as location_city,
        m.accountable_person_id,
        m.accountable_person_name,
        m.effective_from,
        m.effective_to,
        -- previous state
        m.prev_location_code,
        prev_loc.location_name      as prev_location_name,
        m.prev_cost_center_code,
        m.prev_organization_unit_code,
        m.prev_accountable_person_id,
        m.prev_accountable_person_name,
        -- movement type derived from what changed
        case
            when m.prev_location_code is null           then 'INITIAL_ASSIGNMENT'
            when m.location_code != m.prev_location_code then 'LOCATION_CHANGE'
            when m.cost_center_code != m.prev_cost_center_code then 'COST_CENTER_CHANGE'
            when m.accountable_person_id != m.prev_accountable_person_id then 'CUSTODIAN_CHANGE'
            else 'OTHER_CHANGE'
        end                         as movement_type,
        m.business_ts,
        m.technical_ts
    from with_lag m
    left join assets a
        on a.asset_id = m.asset_id
    left join {{ ref('REFD_LOC_V') }} loc
        on loc.location_code = m.location_code
    left join {{ ref('REFD_LOC_V') }} prev_loc
        on prev_loc.location_code = m.prev_location_code
    left join {{ ref('REFD_CC_V') }} cc
        on cc.cost_center_code = m.cost_center_code

)

select * from final
