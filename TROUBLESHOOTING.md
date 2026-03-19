# Troubleshooting Guide

Common issues and how to fix them.

## "Missing required parameter: client_id" Error

This error means Docker cannot find your Google OAuth credentials.

### Quick Fix

1. **Check if `.env` file exists:**
   ```bash
   ls -la backend/.env
   ```
   If it doesn't exist, create it:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Add your Google OAuth credentials to `backend/.env`:**
   ```bash
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-secret
   ```

3. **Rebuild and restart Docker:**
   ```bash
   docker-compose down
   docker-compose up --build backend
   ```

### Detailed Diagnosis

Run the diagnostic script:
```bash
bash backend/check_env.sh
```

This will check:
- ✅ If `backend/.env` exists
- ✅ If `GOOGLE_CLIENT_ID` is set
- ✅ If `GOOGLE_CLIENT_SECRET` is set
- ✅ If Docker can see the environment variables
- ⚠️  Common formatting issues

### Common Causes

#### 1. `.env` file in wrong location

**Wrong:**
```
.env                    # ❌ In root directory
ai-persona-app/.env     # ❌ In project root
```

**Correct:**
```
backend/.env            # ✅ Inside backend directory
```

#### 2. Missing or empty values

**Wrong:**
```bash
GOOGLE_CLIENT_ID=       # ❌ Empty value
# GOOGLE_CLIENT_ID=123  # ❌ Commented out
```

**Correct:**
```bash
GOOGLE_CLIENT_ID=165253565762-jbct22aplamb3j3ppf2aa1pgk776jsmg.apps.googleusercontent.com
```

#### 3. Incorrect formatting

**Wrong:**
```bash
GOOGLE_CLIENT_ID = your-id    # ❌ Spaces around =
GOOGLE_CLIENT_ID: your-id     # ❌ Using colon instead of =
"GOOGLE_CLIENT_ID"=your-id    # ❌ Quoted variable name
```

**Correct:**
```bash
GOOGLE_CLIENT_ID=your-id      # ✅ No spaces, no quotes on variable name
```

#### 4. Docker using old image

If you added the `.env` file after building the Docker image:

```bash
# Stop containers
docker-compose down

# Rebuild from scratch
docker-compose build --no-cache backend

# Start again
docker-compose up backend
```

#### 5. File permissions issue

Make sure the `.env` file is readable:
```bash
chmod 644 backend/.env
```

### Verify it's working

After fixing, check if Docker can see the variables:

```bash
# Check inside running container
docker exec ai_focus_groups_backend printenv | grep GOOGLE

# Should output:
# GOOGLE_CLIENT_ID=165253565762-...
# GOOGLE_CLIENT_SECRET=GOCSPX-...
# GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google
```

### Still not working?

1. **Check the actual file content:**
   ```bash
   cat backend/.env | grep GOOGLE
   ```

2. **Check docker-compose logs:**
   ```bash
   docker-compose logs backend | grep -i "client_id\|oauth\|google"
   ```

3. **Verify the file is being loaded:**
   ```bash
   docker-compose config | grep -A 5 "env_file"
   ```

---

## Database Connection Errors

### "relation 'users' does not exist"

The database tables haven't been created automatically.

**Quick Fix (Docker):**

```bash
# Method 1: Restart with rebuild to run entrypoint script
docker-compose down
docker-compose up --build backend

# Method 2: Manually initialize while backend is running
docker-compose exec backend python -c "from app.database import init_db; init_db(); print('✅ Tables created!')"

# Method 3: Check logs to see if entrypoint failed
docker-compose logs backend | grep -i "database\|error\|table"
```

**Quick Fix (Local development):**
```bash
./venv/bin/python init_db.py
```

**Why this happens:**
- The `docker-entrypoint.sh` should auto-create tables on startup
- If you see this error, the entrypoint might not be running
- Check logs with: `docker-compose logs backend`

**Verify tables were created:**
```bash
# Check if users table exists
docker-compose exec backend python -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)
if 'users' in tables:
    print('✅ users table exists')
else:
    print('❌ users table NOT FOUND')
"
```

### "password authentication failed for user"

PostgreSQL credentials are wrong.

**Fix for Docker:**
Docker Compose automatically sets these - just restart:
```bash
docker-compose down -v  # -v removes volumes
docker-compose up backend
```

**Fix for local development:**
Use SQLite instead in `backend/.env`:
```bash
DATABASE_URL=sqlite:///./ai_focus_groups.db
```

---

## OAuth Flow Errors

### "Error 400: redirect_uri_mismatch"

Your Google Cloud Console redirect URI doesn't match.

**Fix:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Edit your OAuth 2.0 Client ID
3. Add to "Authorized redirect URIs":
   ```
   http://localhost:8000/auth/callback/google
   ```
4. Make sure there are NO trailing slashes

### "Error 403: access_denied" or "This app is not verified"

You're not added as a test user.

**Fix:**
1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Scroll to "Test users"
3. Add your Google email address

---

## Port Already in Use

### "Port 8000 is already allocated"

Another service is using port 8000.

**Fix Option 1 - Stop the other service:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it (use PID from above)
kill -9 <PID>
```

**Fix Option 2 - Use a different port:**
Edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead
```

Then access at `http://localhost:8001`

---

## Tests Failing

### Run tests to verify everything works:

```bash
# All Phase 2 auth tests
pytest tests/unit/test_oauth_handler.py tests/unit/test_auth_middleware.py tests/unit/test_user_model_oauth.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# In Docker
docker-compose exec backend pytest tests/ -v
```

All 28 Phase 2 tests should pass ✅

---

## Need More Help?

1. Run the diagnostic script:
   ```bash
   bash backend/check_env.sh
   ```

2. Check the logs:
   ```bash
   docker-compose logs backend
   ```

3. Verify your setup matches [OAUTH_SETUP_GUIDE.md](backend/OAUTH_SETUP_GUIDE.md)
