{{ config(materialized='table') }}

with depr as (

    select * from {{ ref('DEPR_t1_T') }}

),

assets as (

    select
        asset_id, asset_number, asset_type, category_code,
        asset_name, acquisition_amount, currency_code,
        depreciation_rate, accounting_method
    from {{ ref('ASST_t1_T') }}

),

periods as (

    select
        period_code, fiscal_year, fiscal_period,
        starts_on, ends_on
    from {{ ref('PCAL_t1_T') }}

),

enriched as (

    select
        d.run_item_id,
        d.depreciation_run_id,
        d.run_number,
        d.period_code,
        p.fiscal_year,
        p.fiscal_period,
        p.starts_on                 as period_starts_on,
        p.ends_on                   as period_ends_on,
        d.asset_id,
        a.asset_number,
        a.asset_type,
        a.category_code,
        cat.category_name,
        a.asset_name,
        a.acquisition_amount,
        a.currency_code,
        a.depreciation_rate,
        a.accounting_method,
        d.initiated_by,
        d.depreciation_amount,
        d.item_status,
        d.run_status,
        d.completed_at,
        d.business_ts,
        d.technical_ts
    from depr d
    left join assets  a   on a.asset_id       = d.asset_id
    left join periods p   on p.period_code    = d.period_code
    left join {{ ref('REFD_CAT_V') }} cat
        on cat.category_code = a.category_code

),

final as (

    select
        *,
        sum(depreciation_amount) over (
            partition by asset_id
            order by period_starts_on
            rows between unbounded preceding and current row
        ) as cumulative_depreciation
    from enriched

)

select * from final
