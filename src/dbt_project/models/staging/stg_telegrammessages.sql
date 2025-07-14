-- Staging SQL
{{
  config(
    materialized='incremental',
    unique_key='message_key',
    incremental_strategy='merge',
    merge_update_columns=['message_text', 'has_media', 'image_path'],
    indexes=[
      {'columns': ['message_date'], 'type': 'brin'},
      {'columns': ['channel'], 'type': 'hash'}
    ]
  )
}}

WITH raw_messages AS (
    SELECT
        id AS raw_id,
        scraped_date,
        channel,
        message_id,
        message_date,
        message_text,
        has_media,
        image_path,
        raw_data
    FROM {{ source('raw', 'telegram_messages') }}
    {% if is_incremental() %}
    WHERE message_date > (SELECT MAX(message_date) FROM {{ this }})
    {% endif %}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['raw_id']) }} AS message_key,
    raw_id,
    scraped_date,
    channel,
    message_id,
    message_date,
    message_text,
    has_media,
    image_path,
    raw_data
FROM raw_messages