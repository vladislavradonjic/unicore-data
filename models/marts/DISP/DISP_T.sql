{{ config(materialized='table') }}

-- Disposal register (Registar otpisa) — disposed and written-off assets
-- with their operation request and workflow case details.
-- Joins WFCS via aggregate_id = request_id (aggregate_type = 'AssetOperationRequest').

with disposed_assets as (

    select * from {{ ref('ASST_t1_T') }}
    where lifecycle_status in ('DISPOSED', 'SOLD', 'DONATED')

),

disposal_requests as (

    select * from {{ ref('ASOP_t1_T') }}
    where operation_type = 'DISPOSAL'

),

disposal_cases as (

    select * from {{ ref('WFCS_t1_T') }}
    where aggregate_type = 'AssetOperationRequest'

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
        a.currency_code,
        a.acquisition_amount,
        a.gross_amount,
        a.accumulated_depreciation,
        a.net_amount                as net_book_value_at_disposal,
        req.request_id,
        req.request_number,
        req.operation_type          as disposal_type,
        req.requested_effective_date as disposal_date,
        req.created_by              as requested_by,
        req.verified_by,
        req.verified_at,
        wf.case_id,
        wf.case_number,
        wf.workflow_status,
        wf.maker_username,
        wf.checker_username,
        coalesce(req.business_ts, a.business_ts) as business_ts,
        current_timestamp           as technical_ts
    from disposed_assets a
    left join disposal_requests req on req.asset_id = a.asset_id
    left join disposal_cases    wf  on wf.aggregate_id = req.request_id
    left join {{ ref('REFD_CAT_V') }} cat
        on cat.category_code = a.category_code

)

select * from final
