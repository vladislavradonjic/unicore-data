{{ config(materialized='table') }}

with ranked as (

    select
        *,
        row_number() over (
            partition by cost_center_code, category_code, period_code
            order by business_ts desc, technical_ts desc
        ) as rn
    from {{ ref('CCDA_T') }}
    where business_ts <= current_date - 1

)

select
    period_code, fiscal_year, fiscal_period,
    period_starts_on, period_ends_on,
    cost_center_code, cost_center_name,
    organization_unit_code,
    category_code, category_name,
    asset_count, total_depreciation_amount,
    business_ts, technical_ts
from ranked
where rn = 1
