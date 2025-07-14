-- Dimension dates
{{
  config(
    materialized='table',
    unique_key='date_id'
  )
}}

{% call set_sql_header(config) %}
CREATE EXTENSION IF NOT EXISTS intarray;
{%- endcall %}

WITH date_range AS (
    SELECT 
        MIN(message_date)::DATE AS start_date,
        MAX(message_date)::DATE AS end_date
    FROM {{ ref('stg_telegram_messages') }}
),

date_series AS (
    SELECT generate_series(
        (SELECT start_date FROM date_range),
        (SELECT end_date FROM date_range),
        '1 day'::INTERVAL
    ) AS date
)

SELECT
    TO_CHAR(date, 'YYYYMMDD')::INTEGER AS date_id,
    date AS full_date,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(QUARTER FROM date) AS quarter,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(DAY FROM date) AS day,
    EXTRACT(ISODOW FROM date) AS day_of_week,
    TO_CHAR(date, 'Day') AS day_name,
    CASE WHEN EXTRACT(ISODOW FROM date) IN (6,7) THEN TRUE ELSE FALSE END AS is_weekend,
    EXTRACT(WEEK FROM date) AS week_of_year,
    CASE 
        WHEN EXTRACT(MONTH FROM date) = 1 AND EXTRACT(DAY FROM date) = 7 THEN 'Ethiopian Christmas'
        WHEN EXTRACT(MONTH FROM date) = 1 AND EXTRACT(DAY FROM date) = 19 THEN 'Timket'
        WHEN EXTRACT(MONTH FROM date) = 3 AND EXTRACT(DAY FROM date) = 2 THEN 'Adwa Victory Day'
        ELSE 'Normal day'
    END AS ethiopian_holiday
FROM date_series