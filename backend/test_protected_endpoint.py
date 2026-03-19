#!/usr/bin/env python3
"""
Test Protected Endpoint

Simple script to test accessing /users/me with a JWT token.

Usage:
    python test_protected_endpoint.py YOUR_JWT_TOKEN
"""

import sys
import requests

def test_protected_endpoint(token):
    """Test the /users/me endpoint with a JWT token"""

    print("=" * 60)
    print("  Testing Protected Endpoint: /users/me")
    print("=" * 60)

    url = "http://localhost:8000/users/me"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\nRequest: GET {url}")
    print(f"Authorization: Bearer {token[:20]}...{token[-20:]}")

    try:
        response = requests.get(url, headers=headers)

        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            print("\n✅ SUCCESS! You're authenticated!")
            print("\nYour User Profile:")
            data = response.json()
            print(f"  ID: {data.get('id')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Name: {data.get('name')}")
            print(f"  Google ID: {data.get('google_id')}")
            if data.get('picture_url'):
                print(f"  Picture: {data.get('picture_url')}")
            print(f"  Created: {data.get('created_at')}")
            print(f"  Updated: {data.get('updated_at')}")
        elif response.status_code == 401:
            print("\n❌ UNAUTHORIZED")
            print(f"Error: {response.json()}")
            print("\nPossible reasons:")
            print("- Token is expired (tokens last 24 hours)")
            print("- Token is invalid or malformed")
            print("- User was deleted from database")
        else:
            print(f"\n❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend")
        print("Make sure the backend is running:")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n" + "=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_protected_endpoint.py YOUR_JWT_TOKEN")
        print("\nTo get a JWT token:")
        print("1. Visit: http://localhost:8000/auth/login/google")
        print("2. Sign in with Google")
        print("3. Copy the 'access_token' from the JSON response")
        sys.exit(1)

    token = sys.argv[1]
    test_protected_endpoint(token)


if __name__ == "__main__":
    main()
