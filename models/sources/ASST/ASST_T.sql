{{
    config(
        materialized = 'incremental',
        incremental_strategy = 'append'
    )
}}

with source_assets as (

    select * from {{ source('asset_svc', 'asset') }}

    {% if is_incremental() %}
    where
        created_at > (select max(technical_ts) from {{ this }})
        or (updated_at is not null
            and updated_at > (select max(technical_ts) from {{ this }}))
    {% endif %}

),

current_book_states as (

    -- join only the open book state record (effective_to is null = current)
    select
        id               as book_state_id,
        asset_id         as bs_asset_id,
        gross_amount,
        accumulated_depreciation,
        net_amount,
        depreciation_rate,
        accounting_method,
        effective_from   as book_state_effective_from
    from {{ source('asset_svc', 'asset_book_state') }}
    where effective_to is null

),

final as (

    select
        -- asset core
        a.id                                                        as asset_id,
        a.asset_number,
        a.asset_type,
        a.category_code,
        a.asset_name,
        a.lifecycle_status,
        a.activation_date,
        a.depreciation_start_date,
        a.currency_code,
        a.acquisition_amount,
        a.book_amount,
        a.created_by,
        a.updated_by,
        -- current book state (null for assets still in preparation)
        b.book_state_id,
        b.gross_amount,
        b.accumulated_depreciation,
        b.net_amount,
        b.depreciation_rate,
        b.accounting_method,
        b.book_state_effective_from,
        -- bi-temporal
        coalesce(a.activation_date, cast(a.created_at as date))     as business_ts,
        current_timestamp                                            as technical_ts,
        'false'                                                      as deleted_flag
    from source_assets        a
    left join current_book_states b on b.bs_asset_id = a.id

)

select * from final
