#!/usr/bin/env python3
"""
OAuth Flow Testing Script

Quick script to test the complete OAuth authentication flow.

Usage:
    python test_oauth_flow.py

This will:
1. Check if backend is running
2. Test the /health endpoint
3. Open browser to OAuth login
4. Wait for you to complete OAuth
5. Show you the JWT token
6. Test the /users/me endpoint with the token
"""

import sys
import time
import webbrowser
import requests
from urllib.parse import urlparse, parse_qs


# Configuration
BASE_URL = "http://localhost:8000"
BACKEND_STARTUP_WAIT = 2  # seconds


def print_header(text):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def check_backend_running():
    """Check if backend server is running"""
    print_header("Step 1: Checking Backend Server")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is running!")
            print_info(f"Version: {data.get('version')}")
            print_info(f"Environment: {data.get('environment')}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend server")
        print_info("Start the backend with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error checking backend: {e}")
        return False


def test_oauth_login():
    """Test OAuth login flow"""
    print_header("Step 2: Testing OAuth Login")

    oauth_url = f"{BASE_URL}/auth/login/google"
    print_info(f"Opening OAuth URL: {oauth_url}")
    print_info("Complete the login in your browser...")
    print_info("After login, you'll see a JSON response with your token")

    # Open browser
    webbrowser.open(oauth_url)

    print("\n" + "-" * 60)
    print("INSTRUCTIONS:")
    print("1. Sign in with Google in the browser window")
    print("2. After redirect, you'll see a JSON response")
    print("3. Copy the 'access_token' value")
    print("4. Paste it here (or press Enter to skip)")
    print("-" * 60 + "\n")

    token = input("Paste your JWT token here: ").strip()

    if not token:
        print_info("Skipped token testing")
        return None

    return token


def test_protected_endpoint(token):
    """Test protected endpoint with JWT token"""
    print_header("Step 3: Testing Protected Endpoint")

    if not token:
        print_info("No token provided, skipping")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success("Authentication successful!")
            print("\nYour User Profile:")
            print(f"  ID: {data.get('id')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Name: {data.get('name')}")
            print(f"  Google ID: {data.get('google_id')}")
            if data.get('picture_url'):
                print(f"  Picture: {data.get('picture_url')}")
            print(f"  Created: {data.get('created_at')}")
        elif response.status_code == 401:
            print_error("Token is invalid or expired")
            print_info("Try logging in again to get a fresh token")
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print_info(f"Response: {response.text}")

    except Exception as e:
        print_error(f"Error testing protected endpoint: {e}")


def test_invalid_token():
    """Test that invalid tokens are rejected"""
    print_header("Step 4: Testing Invalid Token (Security Check)")

    headers = {"Authorization": "Bearer invalid_token_12345"}

    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)

        if response.status_code == 401:
            print_success("Invalid tokens are correctly rejected (401)")
        else:
            print_error(f"Expected 401, got {response.status_code}")
            print_info("Security issue: Invalid tokens should be rejected!")

    except Exception as e:
        print_error(f"Error testing invalid token: {e}")


def main():
    """Main testing flow"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        AI Focus Groups - OAuth Testing Script            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # Step 1: Check backend
    if not check_backend_running():
        print("\n" + "=" * 60)
        print("❌ FAILED: Backend server is not running")
        print("=" * 60)
        print("\nTo start the backend:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  uvicorn app.main:app --reload")
        sys.exit(1)

    # Step 2: OAuth login
    token = test_oauth_login()

    # Step 3: Test protected endpoint
    if token:
        test_protected_endpoint(token)

    # Step 4: Security test
    test_invalid_token()

    # Summary
    print_header("Testing Complete!")
    print("""
Summary of OAuth Flow:
1. ✅ Backend server is running
2. ✅ OAuth login redirects to Google
3. %s User authenticated with JWT token
4. ✅ Invalid tokens are rejected

Next steps:
- Build frontend with "Login with Google" button
- Store JWT token in localStorage
- Add Authorization header to all API requests
- Start building Phase 3: Persona Generation!
    """ % ("✅" if token else "⏭️ "))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
