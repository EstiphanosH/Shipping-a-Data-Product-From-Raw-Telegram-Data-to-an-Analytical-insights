# YOLO object detection
import os
import json
import psycopg2
from dotenv import load_dotenv
from ultralytics import YOLO
from datetime import datetime

load_dotenv()

model = YOLO("yolov8n.pt")

def detect_objects(image_path):
    results = model.predict(source=image_path)
    detections = []
    for result in results:
        for box in result.boxes:
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy[0].tolist()
            })
    return detections

def process_new_images():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    cur = conn.cursor()
    
    # Create detections table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.image_detections (
            detection_id SERIAL PRIMARY KEY,
            message_id INT REFERENCES raw.telegram_messages(id),
            detected_class VARCHAR(100),
            confidence FLOAT,
            bbox JSONB,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Find unprocessed images
    cur.execute("""
        SELECT id, message_data->'media'->>'photo' AS image_path
        FROM raw.telegram_messages
        WHERE id NOT IN (SELECT DISTINCT message_id FROM raw.image_detections)
          AND message_data->'media'->>'photo' IS NOT NULL
    """)
    
    for row in cur.fetchall():
        message_id, image_path = row
        try:
            if not os.path.exists(image_path):
                continue
                
            detections = detect_objects(image_path)
            for detection in detections:
                cur.execute("""
                    INSERT INTO raw.image_detections (message_id, detected_class, confidence, bbox)
                    VALUES (%s, %s, %s, %s)
                """, (message_id, detection["class"], detection["confidence"], json.dumps(detection["bbox"])))
            conn.commit()
        except Exception as e:
            print(f"Error processing image for message {message_id}: {str(e)}")
            conn.rollback()
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    process_new_images()