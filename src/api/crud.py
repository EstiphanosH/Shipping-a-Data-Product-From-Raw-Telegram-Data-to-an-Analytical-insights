# CRUD operations
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_top_products(db: Session, limit: int = 10):
    result = db.execute(text("""
        SELECT 
            UNNEST(REGEXP_MATCHES(message_text, '(?i)\\b(paracetamol|aspirin|antibiotic|vaccine|insulin)\\b')) AS product,
            COUNT(*) AS mention_count
        FROM marts.fct_messages
        GROUP BY product
        ORDER BY mention_count DESC
        LIMIT :limit
    """), {"limit": limit})
    
    return [{"name": row[0], "count": row[1]} for row in result]

def get_channel_activity(db: Session, channel_name: str):
    result = db.execute(text("""
        SELECT 
            TO_CHAR(d.date, 'YYYY-MM-DD') AS date_str,
            COUNT(f.message_id) AS message_count
        FROM marts.fct_messages f
        JOIN marts.dim_channels c ON f.channel_key = c.channel_key
        JOIN marts.dim_dates d ON f.date_key = d.date_key
        WHERE c.channel_name = :channel_name
        GROUP BY d.date
        ORDER BY d.date
    """), {"channel_name": channel_name})
    
    return [{"date": row[0], "count": row[1]} for row in result]

def search_messages(db: Session, query: str, limit: int = 10):
    result = db.execute(text("""
        SELECT 
            f.message_id,
            c.channel_name,
            f.message_text,
            TO_CHAR(f.created_at, 'YYYY-MM-DD HH24:MI') AS created_at_str
        FROM marts.fct_messages f
        JOIN marts.dim_channels c ON f.channel_key = c.channel_key
        WHERE f.message_text ILIKE '%' || :query || '%'
        LIMIT :limit
    """), {"query": query, "limit": limit})
    
    return [
        {
            "message_id": row[0],
            "channel_name": row[1],
            "message_text": row[2],
            "created_at": row[3]
        }
        for row in result
    ]