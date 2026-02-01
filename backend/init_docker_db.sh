#!/bin/bash
# Initialize database tables in Docker container

echo "Initializing database tables in Docker..."
docker-compose exec backend python -c "from app.database import init_db; init_db(); print('✅ Database initialized!')"
