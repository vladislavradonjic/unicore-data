{{ config(materialized='table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by asset_id
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('DISP_T') }}
    where business_ts <= (
        date_trunc('month', current_date) - interval '1 day'
    )::date

)

select
    asset_id, asset_number, asset_type,
    category_code, category_name, asset_name,
    lifecycle_status, activation_date,
    currency_code, acquisition_amount,
    gross_amount, accumulated_depreciation, net_book_value_at_disposal,
    request_id, request_number, disposal_type, disposal_date,
    requested_by, verified_by, verified_at,
    case_id, case_number, workflow_status,
    maker_username, checker_username,
    business_ts, technical_ts
from ranked
where rn = 1
