{{ config(materialized = 'table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by asset_id
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('ASST_T') }}
    where business_ts <= (date_trunc('month', current_date) - interval '1 day')::date
      and deleted_flag = 'false'

)

select
    asset_id, asset_number, asset_type, category_code, asset_name,
    lifecycle_status, activation_date, depreciation_start_date,
    currency_code, acquisition_amount, book_amount,
    created_by, updated_by,
    book_state_id, gross_amount, accumulated_depreciation, net_amount,
    depreciation_rate, accounting_method, book_state_effective_from,
    business_ts, technical_ts, deleted_flag
from ranked
where rn = 1
