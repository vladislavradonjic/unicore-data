{{ config(materialized = 'table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by period_code
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('PCAL_T') }}
    where business_ts <= current_date - 1
      and deleted_flag = 'false'

)

select
    period_id, period_code,
    fiscal_year, fiscal_period,
    starts_on, ends_on,
    locked_flag, lock_reason,
    business_ts, technical_ts, deleted_flag
from ranked
where rn = 1
