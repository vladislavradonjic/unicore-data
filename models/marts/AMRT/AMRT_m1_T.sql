{{ config(materialized='table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by asset_id, period_code
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('AMRT_T') }}
    where business_ts <= (
        date_trunc('month', current_date) - interval '1 day'
    )::date

)

select
    run_item_id, depreciation_run_id, run_number,
    period_code, fiscal_year, fiscal_period,
    period_starts_on, period_ends_on,
    asset_id, asset_number, asset_type,
    category_code, category_name, asset_name,
    acquisition_amount, currency_code,
    depreciation_rate, accounting_method,
    initiated_by, depreciation_amount, cumulative_depreciation,
    item_status, run_status, completed_at,
    business_ts, technical_ts
from ranked
where rn = 1
