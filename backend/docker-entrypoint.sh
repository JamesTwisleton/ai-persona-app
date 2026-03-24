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

# Run schema migrations (idempotent ALTER TABLE for new columns)
echo "Running schema migrations..."
python << END
import sys
import traceback

try:
    from app.database import engine
    with engine.connect() as conn:
        stmts = [
            # Persona social columns
            "ALTER TABLE personas ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT TRUE",
            "ALTER TABLE personas ADD COLUMN IF NOT EXISTS view_count INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE personas ADD COLUMN IF NOT EXISTS upvote_count INTEGER NOT NULL DEFAULT 0",
            # Conversation social columns
            "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT TRUE",
            "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS forked_from_id VARCHAR(6)",
            "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS view_count INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS upvote_count INTEGER NOT NULL DEFAULT 0",
            # User superuser column
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN NOT NULL DEFAULT FALSE",
            # Seed superuser
            "UPDATE users SET is_superuser = TRUE WHERE email = 'ajtwisleton@gmail.com'",
            # Upvotes table
            """
            CREATE TABLE IF NOT EXISTS upvotes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                target_type VARCHAR(20) NOT NULL,
                target_id VARCHAR(6) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT uq_upvote_user_target UNIQUE (user_id, target_type, target_id)
            )
            """,
            "CREATE INDEX IF NOT EXISTS ix_upvotes_user_id ON upvotes(user_id)",
            # Page views table
            """
            CREATE TABLE IF NOT EXISTS page_views (
                id SERIAL PRIMARY KEY,
                target_type VARCHAR(20) NOT NULL,
                target_id VARCHAR(6) NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                ip_hash VARCHAR(64),
                viewed_date DATE NOT NULL DEFAULT CURRENT_DATE,
                CONSTRAINT uq_pageview_daily UNIQUE (target_type, target_id, user_id, ip_hash, viewed_date)
            )
            """,
            "CREATE INDEX IF NOT EXISTS ix_page_views_target_id ON page_views(target_id)",
            # Clear expired DALL-E avatar URLs so they fall back to initials
            # (New avatars are stored as S3 keys starting with "avatars/")
            """
            UPDATE personas
            SET avatar_url = NULL
            WHERE avatar_url IS NOT NULL
              AND avatar_url NOT LIKE 'avatars/%'
              AND avatar_url NOT LIKE 'https://api.dicebear.com%'
            """,
        ]
        for stmt in stmts:
            conn.execute(__import__('sqlalchemy').text(stmt))
        conn.commit()
    print("✅ Schema migrations complete!")
except Exception as e:
    print(f"❌ Migration error: {e}")
    traceback.print_exc()
    sys.exit(1)
END

# Start the application
echo "Starting FastAPI application..."
exec "$@"
