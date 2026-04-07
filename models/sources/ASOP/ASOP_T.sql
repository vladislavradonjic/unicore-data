{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'append'
    )
}}

with source as (

    select * from {{ source('asset_svc', 'asset_operation_request') }}

    {% if is_incremental() %}
    where created_at > (select max(technical_ts) from {{ this }})
    {% endif %}

),

final as (

    select
        id                       as request_id,
        asset_id,
        preparation_id,
        request_number,
        operation_type,
        workflow_status,
        requested_effective_date,
        created_by,
        verified_by,
        verified_at,
        -- bi-temporal
        coalesce(
            requested_effective_date,
            cast(created_at as date)
        )                        as business_ts,
        current_timestamp        as technical_ts,
        'false'                  as deleted_flag
    from source

)

select * from final
