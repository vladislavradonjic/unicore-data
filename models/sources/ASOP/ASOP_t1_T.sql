{{ config(materialized = 'table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by request_number
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('ASOP_T') }}
    where business_ts <= current_date - 1
      and deleted_flag = 'false'

)

select
    request_id, asset_id, preparation_id,
    request_number, operation_type, workflow_status,
    requested_effective_date,
    created_by, verified_by, verified_at,
    business_ts, technical_ts, deleted_flag
from ranked
where rn = 1
