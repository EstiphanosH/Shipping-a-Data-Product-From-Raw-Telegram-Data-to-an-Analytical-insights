-- Test: At least 20% of messages should mention medical products
WITH medical_mentions AS (
    SELECT COUNT(*) FILTER (WHERE mentions_medical = 1) AS medical_count,
           COUNT(*) AS total_count
    FROM {{ ref('fct_messages') }}
)

SELECT *
FROM medical_mentions
WHERE medical_count::FLOAT / NULLIF(total_count, 0) < 0.2