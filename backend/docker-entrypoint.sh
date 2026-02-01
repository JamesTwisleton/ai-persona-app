#!/bin/bash
# Docker entrypoint script to initialize database on startup

set -e

echo "Starting AI Focus Groups Backend..."

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
python << END
import time
import psycopg2
import os

db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgresql"):
    # Extract connection details from DATABASE_URL
    # Format: postgresql://user:password@host:port/dbname
    parts = db_url.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_port_db = parts[1].split("/")
    host_port = host_port_db[0].split(":")

    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else "5432"
    dbname = host_port_db[1]

    for i in range(30):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            conn.close()
            print("✅ PostgreSQL is ready!")
            break
        except psycopg2.OperationalError:
            print(f"Waiting for PostgreSQL... ({i+1}/30)")
            time.sleep(1)
    else:
        print("❌ Failed to connect to PostgreSQL after 30 seconds")
        exit(1)
END

# Initialize database tables if they don't exist
echo "Initializing database tables..."
python << END
import sys
import traceback

try:
    from app.database import init_db, engine
    from sqlalchemy import inspect

    # Initialize tables
    init_db()

    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'users' in tables:
        print("✅ Database initialized successfully!")
        print(f"   Tables created: {', '.join(tables)}")
    else:
        print("⚠️  WARNING: 'users' table not found after initialization!")
        print(f"   Tables found: {', '.join(tables)}")
        sys.exit(1)

except Exception as e:
    print(f"❌ ERROR initializing database: {e}")
    traceback.print_exc()
    sys.exit(1)
END

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed! Exiting..."
    exit 1
fi

# Start the application
echo "Starting FastAPI application..."
exec "$@"
