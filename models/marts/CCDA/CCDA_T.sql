{{ config(materialized='table') }}

-- Cost centre depreciation allocation (Amortizacija po centrima troška).
-- Matches each depreciation run item to the assignment active at the start
-- of that period, then aggregates by (cost_center, category, period).

with depr as (

    select * from {{ ref('DEPR_t1_T') }}

),

periods as (

    select period_code, fiscal_year, fiscal_period, starts_on, ends_on
    from {{ ref('PCAL_t1_T') }}

),

depr_with_period as (

    select
        d.run_item_id,
        d.asset_id,
        d.period_code,
        d.depreciation_amount,
        d.business_ts,
        d.technical_ts,
        p.fiscal_year,
        p.fiscal_period,
        p.starts_on             as period_starts_on,
        p.ends_on               as period_ends_on
    from depr d
    left join periods p on p.period_code = d.period_code

),

-- For each depreciation item, find the assignment that was active at the
-- start of the depreciation period. Use the latest effective_from <= period_starts_on.
assignment_for_period as (

    select
        d.run_item_id,
        a.cost_center_code,
        a.organization_unit_code,
        a.location_code,
        row_number() over (
            partition by d.run_item_id
            order by a.effective_from desc
        ) as rn
    from depr_with_period d
    join {{ ref('ASGN_t1_T') }} a
        on  a.asset_id      = d.asset_id
        and a.effective_from <= d.period_starts_on
        and (a.effective_to is null or a.effective_to >= d.period_starts_on)

),

depr_allocated as (

    select
        d.*,
        ap.cost_center_code,
        ap.organization_unit_code,
        ap.location_code
    from depr_with_period d
    left join assignment_for_period ap
        on ap.run_item_id = d.run_item_id and ap.rn = 1

),

assets as (

    select asset_id, category_code
    from {{ ref('ASST_t1_T') }}

),

final as (

    select
        da.period_code,
        da.fiscal_year,
        da.fiscal_period,
        da.period_starts_on,
        da.period_ends_on,
        da.cost_center_code,
        cc.cost_center_name,
        da.organization_unit_code,
        a.category_code,
        cat.category_name,
        count(distinct da.asset_id)     as asset_count,
        sum(da.depreciation_amount)     as total_depreciation_amount,
        max(da.business_ts)             as business_ts,
        current_timestamp               as technical_ts
    from depr_allocated da
    left join assets a
        on a.asset_id = da.asset_id
    left join {{ ref('REFD_CC_V') }}  cc
        on cc.cost_center_code = da.cost_center_code
    left join {{ ref('REFD_CAT_V') }} cat
        on cat.category_code = a.category_code
    group by
        da.period_code, da.fiscal_year, da.fiscal_period,
        da.period_starts_on, da.period_ends_on,
        da.cost_center_code, cc.cost_center_name,
        da.organization_unit_code,
        a.category_code, cat.category_name

)

select * from final
