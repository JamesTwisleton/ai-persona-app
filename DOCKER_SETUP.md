# Running with Docker

Quick guide to run the backend with Docker.

## Prerequisites

- Docker and Docker Compose installed
- `.env` file configured with Google OAuth credentials

## Start the Backend with Docker

```bash
# Start backend + PostgreSQL database
docker-compose up backend

# Or run in background
docker-compose up -d backend
```

This will:
1. ✅ Build the Docker image (first time only)
2. ✅ Start PostgreSQL database
3. ✅ Load environment variables from `backend/.env`
4. ✅ Start the FastAPI backend on `http://localhost:8000`

## Initialize Database Tables

The first time you run with Docker, you need to create the database tables:

```bash
# Run the init script inside the Docker container
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

Or create a user by completing the OAuth flow - it will auto-create tables.

## Test OAuth Flow

1. **Visit in browser:**
   ```
   http://localhost:8000/auth/login/google
   ```

2. **Sign in with Google**

3. **You'll get a JWT token** in the response

4. **Test protected endpoint:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/users/me
   ```

## Useful Commands

```bash
# View logs
docker-compose logs -f backend

# Check database tables
docker-compose exec backend python check_users.py

# Run tests
docker-compose exec backend pytest -v

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build backend

# Clean up everything (including database)
docker-compose down -v
```

## Environment Variables

Docker Compose loads variables from `backend/.env` and overrides:
- `DATABASE_URL` → PostgreSQL (db service)
- `FRONTEND_URL` → http://localhost:3000

All other variables (Google OAuth, JWT secret, etc.) are loaded from `.env`.

## Troubleshooting

### "Missing required parameter: client_id"
- Make sure `backend/.env` exists and has `GOOGLE_CLIENT_ID` set
- Restart containers: `docker-compose restart backend`

### Database connection errors
- Make sure PostgreSQL is healthy: `docker-compose ps`
- Initialize tables: `docker-compose exec backend python -c "from app.database import init_db; init_db()"`

### Port already in use (8000)
- Stop local backend server first
- Or change port in docker-compose.yml: `ports: - "8001:8000"`
