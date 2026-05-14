SELECT

    stm.message_id,

    dc.channel_key,

    TO_CHAR(stm.message_date, 'YYYYMMDD')::INTEGER AS date_key,

    stm.message_text,

    stm.message_length,

    stm.view_count,

    stm.forward_count,

    stm.has_image

FROM {{ ref('stg_telegram_messages') }} stm

LEFT JOIN {{ ref('dim_channels') }} dc
    ON stm.channel_name = dc.channel_name