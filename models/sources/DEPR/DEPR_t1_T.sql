{{ config(materialized = 'table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by run_item_id
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('DEPR_T') }}
    where business_ts <= current_date - 1
      and deleted_flag = 'false'

)

select
    run_item_id, depreciation_run_id,
    run_number, period_code, run_status, completed_at, initiated_by,
    asset_id, asset_number,
    depreciation_amount, item_status,
    business_ts, technical_ts, deleted_flag
from ranked
where rn = 1
