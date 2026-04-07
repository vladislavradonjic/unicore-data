{{ config(materialized = 'table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by assignment_id
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('ASGN_T') }}
    where business_ts <= (date_trunc('month', current_date) - interval '1 day')::date
      and deleted_flag = 'false'

)

select
    assignment_id, asset_id,
    organization_unit_code, cost_center_code, location_code,
    accountable_person_id, accountable_person_name,
    effective_from, effective_to,
    business_ts, technical_ts, deleted_flag
from ranked
where rn = 1
