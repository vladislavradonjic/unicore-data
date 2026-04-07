{{ config(materialized='table') }}

-- Depreciation projection (Projekcija amortizacije) — forward-looking 36-month
-- projection per active asset. Uses generate_series (Postgres-specific).
-- Monthly depreciation = gross_amount × rate / 100 / 12.
-- Projection stops when net_amount would reach zero (asset fully depreciated).
-- No output ports — consumers query directly.

with active_assets as (

    select
        asset_id,
        asset_number,
        asset_type,
        category_code,
        asset_name,
        currency_code,
        depreciation_rate,
        accounting_method,
        gross_amount,
        accumulated_depreciation,
        net_amount,
        depreciation_start_date
    from {{ ref('ASST_t1_T') }}
    where lifecycle_status = 'ACTIVE'
      and net_amount > 0
      and depreciation_rate > 0

),

projection_months as (

    select generate_series(
        date_trunc('month', current_date + interval '1 month')::date,
        date_trunc('month', current_date + interval '36 months')::date,
        interval '1 month'
    )::date as proj_month_start

),

projected as (

    select
        a.asset_id,
        a.asset_number,
        a.asset_type,
        a.category_code,
        a.asset_name,
        a.currency_code,
        a.depreciation_rate,
        a.accounting_method,
        a.gross_amount,
        a.accumulated_depreciation  as accumulated_depreciation_today,
        a.net_amount                as net_amount_today,
        p.proj_month_start,
        to_char(p.proj_month_start, 'YYYY-MM') as projected_period_code,
        -- months elapsed in projection from today
        (
            extract(year from p.proj_month_start) * 12 + extract(month from p.proj_month_start)
            - extract(year from current_date) * 12 - extract(month from current_date)
        )::integer                  as months_from_today,
        -- monthly depreciation charge
        round(
            a.gross_amount * a.depreciation_rate / 100 / 12,
            2
        )                           as monthly_depreciation_amount,
        -- projected net value at end of period
        greatest(
            0,
            a.net_amount - round(
                a.gross_amount * a.depreciation_rate / 100 / 12,
                2
            ) * (
                extract(year from p.proj_month_start) * 12 + extract(month from p.proj_month_start)
                - extract(year from current_date) * 12 - extract(month from current_date)
            )
        )                           as projected_net_amount,
        current_date                as projection_base_date,
        current_timestamp           as technical_ts
    from active_assets a
    cross join projection_months p

),

-- filter out periods where the asset would already be fully depreciated
final as (

    select *
    from projected
    where (
        accumulated_depreciation_today
        + monthly_depreciation_amount * months_from_today
    ) <= gross_amount

)

select * from final
