#!/usr/bin/env python3
"""
Check Users in Database

Quick script to see if OAuth created any users.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User

def main():
    print("=" * 60)
    print("  Users in Database")
    print("=" * 60)

    db = SessionLocal()
    try:
        users = db.query(User).all()

        if not users:
            print("\n❌ No users found in database")
            print("\nThis means OAuth hasn't been completed yet.")
            print("\nTo create a user:")
            print("1. Visit: http://localhost:8000/auth/login/google")
            print("2. Sign in with Google")
            print("3. Complete the OAuth flow")
        else:
            print(f"\n✅ Found {len(users)} user(s):\n")
            for user in users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Name: {user.name}")
                print(f"Google ID: {user.google_id}")
                print(f"Created: {user.created_at}")
                print("-" * 60)

    finally:
        db.close()

    print()


if __name__ == "__main__":
    main()
