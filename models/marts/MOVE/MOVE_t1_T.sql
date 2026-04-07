{{ config(materialized='table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by assignment_id
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('MOVE_T') }}
    where business_ts <= current_date - 1

)

select
    assignment_id, asset_id, asset_number, asset_type,
    category_code, asset_name,
    organization_unit_code, cost_center_code, cost_center_name,
    location_code, location_name, location_city,
    accountable_person_id, accountable_person_name,
    effective_from, effective_to,
    prev_location_code, prev_location_name,
    prev_cost_center_code, prev_organization_unit_code,
    prev_accountable_person_id, prev_accountable_person_name,
    movement_type,
    business_ts, technical_ts
from ranked
where rn = 1
