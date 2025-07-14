-- Fact messages
{{
  config(
    materialized='incremental',
    unique_key='message_key',
    incremental_strategy='merge',
    merge_update_columns=['message_text', 'has_media', 'image_path'],
    indexes=[
      {'columns': ['message_date'], 'type': 'brin'},
      {'columns': ['channel_id'], 'type': 'hash'}
    ]
  )
}}

WITH messages AS (
    SELECT
        m.message_key,
        m.message_id,
        m.channel,
        m.message_date,
        m.message_text,
        m.has_media,
        m.image_path,
        LENGTH(m.message_text) AS message_length,
        array_length(regexp_split_to_array(m.message_text, '\s+'), 1) AS word_count,
        (m.message_text ~* 'paracetamol')::INT AS mentions_paracetamol,
        (m.message_text ~* 'antibiotic')::INT AS mentions_antibiotic,
        (m.message_text ~* 'insulin')::INT AS mentions_insulin
    FROM {{ ref('stg_telegram_messages') }} m
    {% if is_incremental() %}
    WHERE m.message_date > (SELECT MAX(message_date) FROM {{ this }})
    {% endif %}
)

SELECT
    m.message_key,
    c.channel_id,
    d.date_id,
    m.message_id,
    m.message_date,
    m.message_text,
    m.message_length,
    m.word_count,
    m.has_media,
    m.image_path,
    m.mentions_paracetamol,
    m.mentions_antibiotic,
    m.mentions_insulin,
    CASE 
        WHEN m.mentions_paracetamol = 1 OR m.mentions_antibiotic = 1 OR m.mentions_insulin = 1 
        THEN 1 ELSE 0 
    END AS mentions_medical
FROM messages m
JOIN {{ ref('dim_channels') }} c ON m.channel = c.channel_name
JOIN {{ ref('dim_dates') }} d ON m.message_date::DATE = d.full_date