SELECT
    CAST(message_id AS BIGINT) AS message_id,

    LOWER(TRIM(channel_name)) AS channel_name,

    TRIM(message_text) AS message_text,

    CAST(message_date AS TIMESTAMP) AS message_date,

    CAST(view_count AS INTEGER) AS view_count,

    CAST(forward_count AS INTEGER) AS forward_count,

    image_url,

    LENGTH(message_text) AS message_length,

    CASE
        WHEN image_url IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS has_image

FROM raw_telegram_messages

WHERE message_text IS NOT NULL
  AND TRIM(message_text) <> ''