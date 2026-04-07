{{ config(materialized='table') }}

with assets as (

    select * from {{ ref('ASST_t1_T') }}

),

current_assignments as (

    select *,
        row_number() over (
            partition by asset_id
            order by
                case when effective_to is null then 0 else 1 end,
                effective_from desc
        ) as rn
    from {{ ref('ASGN_t1_T') }}

),

final as (

    select
        a.asset_id,
        a.asset_number,
        a.asset_type,
        a.category_code,
        cat.category_name,
        a.asset_name,
        a.lifecycle_status,
        a.activation_date,
        a.depreciation_start_date,
        a.currency_code,
        a.acquisition_amount,
        a.gross_amount,
        a.accumulated_depreciation,
        a.net_amount,
        a.depreciation_rate,
        a.accounting_method,
        asgn.assignment_id,
        asgn.organization_unit_code,
        asgn.cost_center_code,
        cc.cost_center_name,
        asgn.location_code,
        loc.location_name,
        loc.city                    as location_city,
        asgn.accountable_person_id,
        asgn.accountable_person_name,
        asgn.effective_from         as assignment_effective_from,
        a.business_ts,
        current_timestamp           as technical_ts
    from assets a
    left join current_assignments asgn
        on asgn.asset_id = a.asset_id and asgn.rn = 1
    left join {{ ref('REFD_CAT_V') }} cat
        on cat.category_code = a.category_code
    left join {{ ref('REFD_LOC_V') }} loc
        on loc.location_code = asgn.location_code
    left join {{ ref('REFD_CC_V') }}  cc
        on cc.cost_center_code = asgn.cost_center_code

)

select * from final
