SELECT *

FROM {{ ref('stg_telegram_messages') }}

WHERE view_count < 0