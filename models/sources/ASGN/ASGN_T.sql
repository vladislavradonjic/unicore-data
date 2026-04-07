{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'append'
    )
}}

with source as (

    select * from {{ source('asset_svc', 'asset_assignment') }}

    {% if is_incremental() %}
    where created_at > (select max(technical_ts) from {{ this }})
    {% endif %}

),

final as (

    select
        id                       as assignment_id,
        asset_id,
        organization_unit_code,
        cost_center_code,
        location_code,
        accountable_person_id,
        accountable_person_name,
        effective_from,
        effective_to,
        -- bi-temporal
        effective_from           as business_ts,
        current_timestamp        as technical_ts,
        'false'                  as deleted_flag
    from source

)

select * from final
