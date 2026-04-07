{{ config(materialized = 'table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by case_number
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('WFCS_T') }}
    where business_ts <= current_date - 1
      and deleted_flag = 'false'

)

select
    case_id, case_number,
    aggregate_type, aggregate_id,
    operation_type, workflow_status,
    maker_user_id, maker_username,
    checker_user_id, checker_username,
    submitted_at, verified_at, returned_at,
    comment_text,
    business_ts, technical_ts, deleted_flag
from ranked
where rn = 1
