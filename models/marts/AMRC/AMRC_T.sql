{{ config(materialized='table') }}

-- Calculated depreciation control (Obračunata amortizacija — kontrola).
-- Independently recalculates straight-line (PROPORTIONAL) monthly depreciation
-- from first principles: gross_amount × rate / 100 / 12, capped at remaining
-- book value. Joined to AMRT_t1_T to expose ERP vs platform variance.
--
-- Limitations:
--   - Uses current gross_amount; value increases mid-life will cause a mismatch
--     for prior periods (by design — flags the discrepancy for investigation).
--   - First/last partial periods not prorated (same convention as ERP seeder).
--   - PROPORTIONAL method only; DEGRESSIVE not implemented.

with assets as (

    select
        asset_id, asset_number, asset_type, category_code, asset_name,
        currency_code, gross_amount, net_amount, accumulated_depreciation,
        depreciation_rate, accounting_method, depreciation_start_date
    from {{ ref('ASST_t1_T') }}
    where depreciation_rate > 0
      and gross_amount      > 0

),

disposal_dates as (

    select asset_id, min(requested_effective_date) as disposal_date
    from {{ ref('ASOP_t1_T') }}
    where operation_type = 'DISPOSAL'
    group by asset_id

),

assets_ext as (

    select a.*, d.disposal_date
    from assets a
    left join disposal_dates d on d.asset_id = a.asset_id

),

periods as (

    select period_code, fiscal_year, fiscal_period, starts_on, ends_on
    from {{ ref('PCAL_t1_T') }}

),

-- cross product filtered to periods when the asset was being depreciated
asset_periods as (

    select
        a.asset_id,
        a.asset_number,
        a.category_code,
        a.asset_name,
        a.currency_code,
        a.gross_amount,
        a.depreciation_rate,
        a.accounting_method,
        a.disposal_date,
        p.period_code,
        p.fiscal_year,
        p.fiscal_period,
        p.starts_on                 as period_starts_on,
        p.ends_on                   as period_ends_on,
        -- how many complete periods elapsed before this one
        (
            p.fiscal_year  * 12 + p.fiscal_period
            - cast(extract(year  from a.depreciation_start_date) as integer) * 12
            - cast(extract(month from a.depreciation_start_date) as integer)
        )                           as periods_elapsed
    from assets_ext a
    cross join periods p
    where a.depreciation_start_date <= p.starts_on
      and (a.disposal_date is null or a.disposal_date >= p.starts_on)

),

calculated as (

    select
        *,
        -- constant monthly charge for proportional method
        round(gross_amount * depreciation_rate / 100 / 12, 2)
            as monthly_charge,
        -- book value remaining at the start of this period
        greatest(
            cast(0 as numeric),
            gross_amount
            - round(gross_amount * depreciation_rate / 100 / 12, 2) * periods_elapsed
        )                           as remaining_at_period_start
    from asset_periods

),

with_cap as (

    select
        *,
        -- final calculated amount: capped at remaining (handles last period)
        least(monthly_charge, remaining_at_period_start)
            as calculated_amount
    from calculated
    where remaining_at_period_start > 0

),

reconciled as (

    select
        c.asset_id,
        c.asset_number,
        c.category_code,
        c.asset_name,
        c.currency_code,
        c.gross_amount,
        c.depreciation_rate,
        c.accounting_method,
        c.period_code,
        c.fiscal_year,
        c.fiscal_period,
        c.period_starts_on,
        c.period_ends_on,
        c.periods_elapsed,
        c.monthly_charge,
        c.remaining_at_period_start,
        c.calculated_amount,
        erp.run_item_id,
        erp.run_number,
        erp.depreciation_amount     as erp_amount,
        -- variance: positive = platform calculates more than ERP posted
        c.calculated_amount - coalesce(erp.depreciation_amount, 0)
            as variance,
        case
            when erp.depreciation_amount is null        then 'ERP_MISSING'
            when abs(
                c.calculated_amount
                - erp.depreciation_amount
            ) < cast(0.01 as numeric)                   then 'MATCH'
            else                                             'MISMATCH'
        end                         as reconciliation_status,
        current_timestamp           as technical_ts
    from with_cap c
    left join {{ ref('AMRT_t1_T') }} erp
        on  erp.asset_id    = c.asset_id
        and erp.period_code = c.period_code

)

select * from reconciled
