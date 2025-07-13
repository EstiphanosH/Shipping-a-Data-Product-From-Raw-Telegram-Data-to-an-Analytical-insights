#!/bin/bash

# Load environment variables
source ../.env

# Start the database container
docker-compose -f ../docker/docker-compose.db.yml up -d

# Wait for database to initialize
echo "Waiting for database to start..."
sleep 10

# Verify database creation
docker exec -it telegram_dw_db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 'Database telegram_dw ready' AS status"