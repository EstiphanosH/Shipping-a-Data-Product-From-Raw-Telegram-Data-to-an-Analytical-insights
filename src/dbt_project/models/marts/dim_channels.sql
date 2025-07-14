-- Dimension channels
{{
  config(
    materialized='table',
    unique_key='channel_id',
    indexes=[
      {'columns': ['channel_name'], 'type': 'hash'}
    ]
  )
}}

WITH channel_stats AS (
    SELECT
        channel,
        COUNT(*) AS total_messages,
        COUNT(*) FILTER (WHERE has_media) AS media_count,
        MIN(message_date) AS first_message_date,
        MAX(message_date) AS last_message_date
    FROM {{ ref('stg_telegram_messages') }}
    GROUP BY 1
),

medical_keywords AS (
    SELECT 
        channel,
        COUNT(*) FILTER (WHERE message_text ~* 'paracetamol') AS paracetamol_count,
        COUNT(*) FILTER (WHERE message_text ~* 'antibiotic') AS antibiotic_count,
        COUNT(*) FILTER (WHERE message_text ~* 'insulin') AS insulin_count
    FROM {{ ref('stg_telegram_messages') }}
    GROUP BY 1
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['c.channel']) }} AS channel_id,
    c.channel AS channel_name,
    c.total_messages,
    c.media_count,
    ROUND(c.media_count::FLOAT * 100.0 / NULLIF(c.total_messages, 0), 2) AS media_percentage,
    c.first_message_date,
    c.last_message_date,
    COALESCE(m.paracetamol_count, 0) AS paracetamol_mentions,
    COALESCE(m.antibiotic_count, 0) AS antibiotic_mentions,
    COALESCE(m.insulin_count, 0) AS insulin_mentions
FROM channel_stats c
LEFT JOIN medical_keywords m ON c.channel = m.channel