SELECT
    ROW_NUMBER() OVER () AS channel_key,

    channel_name,

    CASE
        WHEN channel_name ILIKE '%pharma%' THEN 'Pharmaceutical'
        WHEN channel_name ILIKE '%cosmetic%' THEN 'Cosmetics'
        ELSE 'Medical'
    END AS channel_type,

    MIN(message_date) AS first_post_date,

    MAX(message_date) AS last_post_date,

    COUNT(*) AS total_posts,

    AVG(view_count) AS avg_views

FROM {{ ref('stg_telegram_messages') }}

GROUP BY channel_name