#!/bin/bash
# Environment Variable Diagnostic Script
# Helps debug missing GOOGLE_CLIENT_ID and other env vars

echo "======================================================================"
echo "  Environment Variable Diagnostic Tool"
echo "======================================================================"
echo ""

# Check 1: Does .env file exist?
echo "1. Checking if backend/.env file exists..."
if [ -f "backend/.env" ]; then
    echo "   ✅ backend/.env exists"
else
    echo "   ❌ backend/.env NOT FOUND!"
    echo "   Create it by copying: cp backend/.env.example backend/.env"
    exit 1
fi

# Check 2: Does it contain GOOGLE_CLIENT_ID?
echo ""
echo "2. Checking if GOOGLE_CLIENT_ID is set in .env..."
if grep -q "^GOOGLE_CLIENT_ID=" backend/.env; then
    # Get the value (mask it for security)
    VALUE=$(grep "^GOOGLE_CLIENT_ID=" backend/.env | cut -d '=' -f 2 | cut -c 1-20)
    if [ -z "$VALUE" ] || [ "$VALUE" = "" ]; then
        echo "   ❌ GOOGLE_CLIENT_ID is empty!"
        echo "   Add your Google OAuth Client ID from Google Cloud Console"
    else
        echo "   ✅ GOOGLE_CLIENT_ID is set (value: ${VALUE}...)"
    fi
else
    echo "   ❌ GOOGLE_CLIENT_ID not found in .env file!"
    echo "   Add this line: GOOGLE_CLIENT_ID=your-client-id-here"
fi

# Check 3: Does it contain GOOGLE_CLIENT_SECRET?
echo ""
echo "3. Checking if GOOGLE_CLIENT_SECRET is set in .env..."
if grep -q "^GOOGLE_CLIENT_SECRET=" backend/.env; then
    VALUE=$(grep "^GOOGLE_CLIENT_SECRET=" backend/.env | cut -d '=' -f 2 | cut -c 1-20)
    if [ -z "$VALUE" ] || [ "$VALUE" = "" ]; then
        echo "   ❌ GOOGLE_CLIENT_SECRET is empty!"
    else
        echo "   ✅ GOOGLE_CLIENT_SECRET is set (value: ${VALUE}...)"
    fi
else
    echo "   ❌ GOOGLE_CLIENT_SECRET not found in .env file!"
fi

# Check 4: Check for common issues
echo ""
echo "4. Checking for common issues..."

# Check for Windows line endings
if file backend/.env | grep -q "CRLF"; then
    echo "   ⚠️  WARNING: .env file has Windows line endings (CRLF)"
    echo "   Convert to Unix line endings: dos2unix backend/.env"
fi

# Check for spaces around =
if grep -q " = " backend/.env; then
    echo "   ⚠️  WARNING: Found spaces around '=' in .env file"
    echo "   Remove spaces: GOOGLE_CLIENT_ID=value (not GOOGLE_CLIENT_ID = value)"
fi

# Check 5: Test if Docker can see the env vars
echo ""
echo "5. Testing Docker environment (if running)..."
if docker ps | grep -q "ai_focus_groups_backend"; then
    echo "   Backend container is running, checking env vars..."
    CLIENT_ID=$(docker exec ai_focus_groups_backend printenv GOOGLE_CLIENT_ID 2>/dev/null || echo "")
    if [ -z "$CLIENT_ID" ]; then
        echo "   ❌ GOOGLE_CLIENT_ID NOT visible inside Docker container!"
        echo "   Solution: Restart Docker with: docker-compose down && docker-compose up --build backend"
    else
        echo "   ✅ GOOGLE_CLIENT_ID is visible inside Docker: ${CLIENT_ID:0:20}..."
    fi
else
    echo "   ℹ️  Backend container not running"
    echo "   Start it with: docker-compose up backend"
fi

echo ""
echo "======================================================================"
echo "  Diagnostic Complete"
echo "======================================================================"
echo ""
echo "Quick Fixes:"
echo "1. Make sure backend/.env exists and has your Google OAuth credentials"
echo "2. Restart Docker: docker-compose down && docker-compose up --build backend"
echo "3. Check the file with: cat backend/.env | grep GOOGLE"
echo ""
