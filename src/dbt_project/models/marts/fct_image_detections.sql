{{ config(materialized='table') }}

SELECT
    d.detection_id,
    d.message_id,
    d.detected_class,
    d.confidence,
    (d.bbox->>0)::FLOAT AS x_min,
    (d.bbox->>1)::FLOAT AS y_min,
    (d.bbox->>2)::FLOAT AS x_max,
    (d.bbox->>3)::FLOAT AS y_max,
    d.detected_at
FROM raw.image_detections d