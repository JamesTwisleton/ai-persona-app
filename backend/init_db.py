#!/usr/bin/env python3
"""
Database Initialization Script

Quick script to create database tables for local development.

Usage:
    python init_db.py

This will:
1. Create the SQLite database file (if using SQLite)
2. Create all tables defined in the models
3. Verify the tables were created successfully
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import init_db, engine
from app.models.user import User
from sqlalchemy import inspect

def main():
    """Initialize the database"""
    print("=" * 60)
    print("  AI Focus Groups - Database Initialization")
    print("=" * 60)

    # Get database URL
    db_url = engine.url
    print(f"\nDatabase: {db_url}")

    # Create tables
    print("\nCreating database tables...")
    init_db()

    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\n✅ Database initialized successfully!")
    print(f"\nTables created:")
    for table in tables:
        print(f"  - {table}")

    print("\n" + "=" * 60)
    print("✅ Ready to run OAuth flow!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the backend: uvicorn app.main:app --reload")
    print("2. Visit: http://localhost:8000/auth/login/google")
    print("3. Sign in with Google")
    print("4. You should get back a JWT token!")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
