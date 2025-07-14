ER Diagram
    dim_dates ||--o{ fct_messages : "date_key"
    dim_channels ||--o{ fct_messages : "channel_id"
    
    dim_dates {
        date date_key PK
        integer day
        integer month
        integer year
        integer day_of_week
    }
    
    dim_channels {
        bigint channel_id PK
        string channel_name
        string title
        string description
        integer member_count
        timestamp created_at
        timestamp scraped_at
    }
    
    fct_messages {
        bigint message_id PK
        bigint channel_id FK
        date date_key FK
        text message_text
        integer views
        integer forwards
        boolean has_media
        string media_type
        string media_path
        timestamp scraped_at
    }