# Google OAuth Setup & Testing Guide

Complete guide to set up Google OAuth credentials and test the authentication flow.

## Table of Contents
- [Google Cloud Console Setup](#google-cloud-console-setup)
- [Configure Your App](#configure-your-app)
- [Test the OAuth Flow](#test-the-oauth-flow)
- [Common Issues & Troubleshooting](#common-issues--troubleshooting)

---

## Google Cloud Console Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click the project dropdown at the top
4. Click **"New Project"**
   - **Project name**: `AI Focus Groups` (or your preferred name)
   - **Organization**: Leave as default (No organization)
5. Click **"Create"**
6. Wait for the project to be created (~30 seconds)
7. Select your new project from the dropdown

### Step 2: Enable Google+ API (Required for OAuth)

1. In the left sidebar, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google+ API"** or **"Google Identity"**
3. Click on **"Google+ API"**
4. Click **"Enable"**
5. Wait for it to enable (~10 seconds)

### Step 3: Configure OAuth Consent Screen

This is what users see when they log in with Google.

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** (unless you have a Google Workspace)
3. Click **"Create"**

**App Information:**
- **App name**: `AI Focus Groups`
- **User support email**: Your email address
- **App logo**: (Optional - skip for now)
- **Application home page**: `http://localhost:3000` (or your frontend URL)
- **Application privacy policy**: (Optional - can skip for development)
- **Application terms of service**: (Optional - can skip for development)

**Developer contact information:**
- **Email addresses**: Your email address

4. Click **"Save and Continue"**

**Scopes:**
5. Click **"Add or Remove Scopes"**
6. Select these scopes (search for them):
   - `openid`
   - `email`
   - `profile`
   - Alternatively, select:
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
7. Click **"Update"**
8. Click **"Save and Continue"**

**Test Users:**
9. Click **"Add Users"**
10. Add your Google email address (the one you'll use for testing)
11. Click **"Add"**
12. Click **"Save and Continue"**

13. Review the summary and click **"Back to Dashboard"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**

**Application type:**
3. Select **"Web application"**

**Name:**
4. Enter: `AI Focus Groups - Local Development`

**Authorized JavaScript origins:**
5. Click **"Add URI"**
6. Enter: `http://localhost:8000`
7. Click **"Add URI"** again
8. Enter: `http://localhost:3000` (if using frontend)

**Authorized redirect URIs:**
9. Click **"Add URI"**
10. Enter: `http://localhost:8000/auth/callback/google`
11. This MUST match exactly what's in your `.env` file!

12. Click **"Create"**

### Step 5: Copy Your Credentials

A popup will appear with your credentials:

- **Client ID**: Something like `123456789-abcdefg.apps.googleusercontent.com`
- **Client Secret**: Something like `GOCSPX-abc123def456`

**IMPORTANT:** Copy both of these! You'll need them in the next step.

13. Click **"Download JSON"** (optional - for backup)
14. Click **"OK"**

---

## Configure Your App

### Step 1: Create `.env` File

```bash
cd backend

# Copy the example file
cp .env.example .env

# Open the file in your editor
```

### Step 2: Add Your Google OAuth Credentials

Edit `backend/.env` and update these values:

```bash
# Google OAuth 2.0
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google
GOOGLE_SCOPES=openid email profile

# JWT Session Tokens
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Database (PostgreSQL or SQLite for development)
DATABASE_URL=postgresql://ai_focus_groups_user:dev_password@localhost:5432/ai_focus_groups
# Or use SQLite for quick testing:
# DATABASE_URL=sqlite:///./ai_focus_groups.db
```

**Generate a secure JWT secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as your `JWT_SECRET`.

### Step 3: Verify Configuration

```bash
# Check your .env file has the correct values
cat .env | grep GOOGLE
```

You should see your actual Google credentials (not the example values).

---

## Test the OAuth Flow

### Option 1: Quick API Test (Backend Only)

#### 1. Start the Backend Server

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload

# Or use the Python script:
# python -m app.main
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

#### 2. Test the Login Endpoint

**Option A: Using your browser**
1. Open your browser
2. Go to: `http://localhost:8000/auth/login/google`
3. You'll be redirected to Google's login page
4. Sign in with the Google account you added as a test user
5. Grant permissions
6. You'll be redirected back with a JWT token!

**Option B: Using cURL (to see the redirect)**
```bash
curl -v http://localhost:8000/auth/login/google
```

You'll see a `302 Redirect` to Google's OAuth page.

#### 3. Complete the Flow

After signing in with Google:
- Google redirects back to: `http://localhost:8000/auth/callback/google?code=...&state=...`
- Your backend exchanges the code for user info
- You get back a JSON response with JWT token:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "your-email@gmail.com",
    "name": "Your Name",
    "google_id": "google_oauth2|123456789",
    "picture_url": "https://lh3.googleusercontent.com/...",
    "created_at": "2026-01-31T...",
    "updated_at": "2026-01-31T..."
  }
}
```

#### 4. Test the Protected Endpoint

Copy the `access_token` from the response above, then:

```bash
# Replace YOUR_JWT_TOKEN with the actual token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/users/me
```

You should get your user profile back:
```json
{
  "id": 1,
  "email": "your-email@gmail.com",
  "name": "Your Name",
  "google_id": "google_oauth2|123456789",
  "picture_url": "https://...",
  "created_at": "2026-01-31T...",
  "updated_at": "2026-01-31T..."
}
```

#### 5. Test with Invalid Token

```bash
curl -H "Authorization: Bearer invalid_token" \
     http://localhost:8000/users/me
```

You should get a `401 Unauthorized` response:
```json
{
  "detail": "Invalid or expired token"
}
```

### Option 2: Full Stack Test (Backend + Frontend)

When you have the frontend ready:

1. **Start Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Start Frontend:**
```bash
cd frontend
npm run dev
```

3. **Test the Flow:**
   - Go to `http://localhost:3000`
   - Click "Login with Google"
   - Sign in with Google
   - You're redirected back, logged in!
   - Your JWT is stored in localStorage/cookies
   - You can now access protected features

### Option 3: Interactive API Docs

FastAPI provides automatic interactive API documentation:

1. Start the backend server
2. Go to: `http://localhost:8000/docs`
3. You'll see all your API endpoints
4. Try the OAuth flow:
   - Click on `GET /auth/login/google`
   - Click "Try it out"
   - Click "Execute"
   - Follow the OAuth flow in your browser

---

## Common Issues & Troubleshooting

### Issue 1: "Error 400: redirect_uri_mismatch"

**Problem:** The redirect URI in your request doesn't match Google Console.

**Solution:**
1. Check your `.env` file:
   ```bash
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google
   ```
2. Check Google Console → Credentials → Your OAuth Client → Authorized redirect URIs
3. Make sure they EXACTLY match (including `http://` and port)
4. No trailing slashes!

### Issue 2: "Access blocked: This app's request is invalid"

**Problem:** Missing or incorrect scopes in OAuth consent screen.

**Solution:**
1. Go to Google Console → OAuth consent screen
2. Add scopes: `openid`, `email`, `profile`
3. Save and try again

### Issue 3: "Error 403: access_denied"

**Problem:** You're not added as a test user.

**Solution:**
1. Go to Google Console → OAuth consent screen → Test users
2. Add your Google email address
3. Save and try again

### Issue 4: "Invalid authorization code"

**Problem:** OAuth state expired or code was already used.

**Solution:**
- OAuth codes are single-use and expire quickly
- Go back to `/auth/login/google` and start fresh
- Don't refresh the callback page

### Issue 5: Backend won't start - "No module named 'authlib'"

**Problem:** Missing dependencies.

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 6: Database errors when testing

**Problem:** Database not initialized.

**Solution:**
```bash
# Option 1: Use SQLite (quick for testing)
# In .env file:
DATABASE_URL=sqlite:///./ai_focus_groups.db

# Option 2: Start PostgreSQL with Docker
docker-compose up db

# Option 3: Run tests (creates in-memory database)
pytest tests/
```

### Issue 7: "Token expired" immediately

**Problem:** Clock skew or JWT_SECRET changed.

**Solution:**
1. Make sure your system clock is correct
2. Don't change `JWT_SECRET` after issuing tokens
3. Generate a new token by logging in again

### Issue 8: CORS errors in browser

**Problem:** Frontend and backend on different domains.

**Solution:**
Backend already has CORS configured for `http://localhost:3000`.

If using a different frontend URL, update `backend/app/main.py`:
```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://your-frontend-url",  # Add your frontend URL
]
```

---

## Verification Checklist

Before testing, verify:

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] Test user added (your Google email)
- [ ] OAuth 2.0 credentials created
- [ ] Client ID and Client Secret copied
- [ ] `backend/.env` file created
- [ ] `GOOGLE_CLIENT_ID` set in `.env`
- [ ] `GOOGLE_CLIENT_SECRET` set in `.env`
- [ ] `GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google`
- [ ] `JWT_SECRET` generated and set
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend server running (`uvicorn app.main:app --reload`)
- [ ] Can access `http://localhost:8000/docs`

---

## Testing Workflow Summary

```
1. Start backend server
   ↓
2. Browser → http://localhost:8000/auth/login/google
   ↓
3. Redirected to Google → Sign in
   ↓
4. Google redirects back → Callback page
   ↓
5. Get JWT token in response
   ↓
6. Use token for protected requests:
   curl -H "Authorization: Bearer <token>" http://localhost:8000/users/me
   ↓
7. ✅ Success! You're authenticated
```

---

## Next Steps

Once OAuth is working:

1. **Test with automated tests:**
   ```bash
   pytest tests/unit/test_oauth_handler.py -v
   ```

2. **Build the frontend:**
   - Add "Login with Google" button
   - Store JWT token in localStorage
   - Add Authorization header to all API requests

3. **Move to production:**
   - Create production OAuth credentials
   - Update redirect URIs to production domain
   - Use environment variables for secrets (never commit!)
   - Publish OAuth consent screen (verify app with Google)

---

## Security Notes

🔒 **IMPORTANT:**
- Never commit `.env` file to Git (already in `.gitignore`)
- Never share your `GOOGLE_CLIENT_SECRET` publicly
- Never share your `JWT_SECRET` publicly
- Use different credentials for development vs production
- In production, use HTTPS (not HTTP)
- In production, set secure cookies with httpOnly flag

---

## Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [FastAPI OAuth Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Authlib Documentation](https://docs.authlib.org/)

---

**Need help?** Check the [Common Issues](#common-issues--troubleshooting) section or open an issue on GitHub.
