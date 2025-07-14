import os
import json
import logging
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extras import execute_values

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_loader')

def create_raw_schema():
    """Create raw schema and table if not exists"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        with conn.cursor() as cur:
            # Create schema and table
            cur.execute("""
                CREATE SCHEMA IF NOT EXISTS raw;
                CREATE TABLE IF NOT EXISTS raw.telegram_messages (
                    id BIGSERIAL PRIMARY KEY,
                    scraped_date DATE NOT NULL,
                    channel TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    message_date TIMESTAMPTZ NOT NULL,
                    message_text TEXT,
                    has_media BOOLEAN,
                    image_path TEXT,
                    raw_data JSONB NOT NULL,
                    CONSTRAINT unique_message UNIQUE (channel, message_id)
                );
                CREATE INDEX IF NOT EXISTS idx_message_date ON raw.telegram_messages (message_date);
                CREATE INDEX IF NOT EXISTS idx_channel ON raw.telegram_messages (channel);
            """)
            conn.commit()
        logger.info("Created raw schema and table")
    except Exception as e:
        logger.error(f"Schema creation failed: {str(e)}")
        raise
    finally:
        if conn: conn.close()

def load_json_to_postgres():
    """Load JSON files into PostgreSQL efficiently"""
    data_dir = os.path.join(os.getenv('DATA_ROOT', 'data'), 'raw', 'telegram_messages')
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return

    processed_files = set()
    try:
        # Get already processed files
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT raw_data->>'source_file' FROM raw.telegram_messages")
            processed_files = {row[0] for row in cur.fetchall()}
    except Exception as e:
        logger.warning(f"Could not fetch processed files: {str(e)}")

    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        with conn.cursor() as cur:
            for root, _, files in os.walk(data_dir):
                for file in files:
                    if file == 'messages.json':
                        file_path = os.path.join(root, file)
                        if file_path in processed_files:
                            logger.info(f"Skipping already processed: {file_path}")
                            continue
                            
                        path_parts = root.split(os.sep)
                        scraped_date = path_parts[-2]
                        channel = path_parts[-1]
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                        
                        records = []
                        for msg in messages:
                            try:
                                records.append((
                                    scraped_date,
                                    channel,
                                    str(msg['id']),
                                    datetime.fromisoformat(msg['date']),
                                    msg.get('text', ''),
                                    msg.get('media', False),
                                    msg.get('image_path'),
                                    json.dumps(msg),
                                    file_path  # Track source file
                                ))
                            except KeyError as e:
                                logger.error(f"Missing key in message: {str(e)}")
                        
                        # Bulk insert with conflict handling
                        execute_values(
                            cur,
                            """
                            INSERT INTO raw.telegram_messages 
                            (scraped_date, channel, message_id, message_date, 
                             message_text, has_media, image_path, raw_data, source_file)
                            VALUES %s
                            ON CONFLICT (channel, message_id) DO NOTHING
                            """,
                            records
                        )
                        
                        logger.info(f"Loaded {len(records)} messages from {file_path}")
            conn.commit()
    except Exception as e:
        logger.error(f"Data loading failed: {str(e)}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()
    logger.info("Data loading complete")

if __name__ == "__main__":
    load_dotenv()
    create_raw_schema()
    load_json_to_postgres()