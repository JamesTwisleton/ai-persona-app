# PR Preview Environments

## Overview

Every pull request automatically gets a live preview environment deployed to [fly.io](https://fly.io), giving you a full working instance of the app (frontend + backend + database) accessible via a unique URL. This lets you review UI/UX changes from any device (including iPad) without needing to build locally.

## How It Works

### Architecture

Each PR spins up **3 resources** on fly.io:

```
PR #123
  |
  +-- persona-pr-123-be   (FastAPI backend, shared-cpu-1x, 256MB)
  |     |
  |     +-- Fly Postgres   (single-node dev DB, attached to backend)
  |
  +-- persona-pr-123-fe   (Next.js frontend, shared-cpu-1x, 256MB)
        |
        +-- Talks to backend via: https://persona-pr-123-be.fly.dev
```

- **Backend**: Production Dockerfile target, runs uvicorn with 1 worker
- **Frontend**: Production Dockerfile target, built with `NEXT_PUBLIC_API_URL` pointing to the backend's fly.io URL
- **Database**: Fly Postgres dev instance (single node, no HA) -- free, auto-destroyed with the app

### Lifecycle

| Event | Action |
|-------|--------|
| PR opened | Deploy full environment, comment preview URL on PR |
| PR updated (new push) | Re-deploy backend + frontend with latest code |
| PR closed or merged | Destroy all 3 fly apps (backend, frontend, database) |

### What Gets Deployed

- Backend: built from `backend/Dockerfile` (production target)
- Frontend: built from `frontend/Dockerfile` (production target)
- Database: Fly Postgres 15, initialised by `docker-entrypoint.sh` (creates tables + runs migrations)

### Environment & Secrets

The preview environment runs with these secrets (sourced from GitHub Actions secrets):

| Secret | Source | Purpose |
|--------|--------|---------|
| `DATABASE_URL` | Auto-set by Fly Postgres attach | PostgreSQL connection |
| `JWT_SECRET` | Auto-generated per PR | Session tokens |
| `ANTHROPIC_API_KEY` | GitHub secret | Claude API for persona conversations |
| `OPENAI_API_KEY` | GitHub secret | DALL-E avatars + content moderation |
| `GOOGLE_CLIENT_ID` | GitHub secret | Google OAuth |
| `GOOGLE_CLIENT_SECRET` | GitHub secret | Google OAuth |
| `GOOGLE_REDIRECT_URI` | Computed | `https://persona-pr-{N}-be.fly.dev/auth/callback/google` |
| `FRONTEND_URL` | Computed | `https://persona-pr-{N}-fe.fly.dev` |

### Test Mode (Auto-Login)

Preview environments bypass Google OAuth entirely. Instead of requiring a real Google login, the system uses a **test mode** that:

1. **Seeds the database** on startup with sample data (4 personas, 1 conversation with 6 messages)
2. **Auto-logs you in** as a superuser test account when you visit the app

This means you can immediately interact with the full app -- create personas, start conversations, view the discovery feed -- without needing Google OAuth credentials.

#### How it works

- Backend: `ENV=preview` enables a `/auth/test-login` endpoint that returns a JWT for a pre-seeded test superuser. This endpoint returns 404 in all other environments.
- Backend: `seed_preview_data.py` runs during container startup (via `docker-entrypoint.sh`) and populates the database with realistic sample data.
- Frontend: `NEXT_PUBLIC_PREVIEW_MODE=true` is baked in at build time. When the `AuthContext` detects preview mode and no stored token, it automatically calls `/auth/test-login` and stores the returned JWT.

#### Security

- The `/auth/test-login` endpoint is **hard-gated** on `ENV=preview`. It returns 404 in production and development.
- Preview environments are ephemeral and destroyed on PR close. No real user data exists in them.
- The test user (`test@preview.local`) only exists in preview databases.

## Cost

fly.io pricing for the smallest machines:

| Resource | Cost | Notes |
|----------|------|-------|
| shared-cpu-1x (256MB) x2 | ~$0.005/hr each | Backend + frontend |
| Fly Postgres dev | Free | Single node, no HA |
| **Total per PR** | **~$0.01/hr** | ~$0.24/day if left running 24h |

**Typical usage:** If a PR is open for 2 days and you review it for a few hours, cost is well under $1. All resources are destroyed on PR close, so no orphaned costs.

fly.io also auto-stops machines after inactivity (configurable), which can reduce costs further.

## GitHub Actions Workflow

**File:** `.github/workflows/preview-env.yml`

### Trigger

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, closed]
```

### Jobs

1. **`deploy`** (runs on open/sync/reopen):
   - Installs `flyctl`
   - Creates/updates backend fly app + Postgres
   - Sets secrets on backend app
   - Deploys backend from Dockerfile
   - Creates/updates frontend fly app
   - Deploys frontend with `NEXT_PUBLIC_API_URL` pointing to backend
   - Comments the preview URL on the PR (or updates existing comment)

2. **`teardown`** (runs on close):
   - Destroys frontend fly app
   - Destroys backend fly app (Postgres is destroyed with it)

### Required GitHub Secrets

You must have these secrets configured in your GitHub repository settings:

| Secret | Required | Notes |
|--------|----------|-------|
| `FLY_API_TOKEN` | Yes | fly.io API token for deployments |
| `ANTHROPIC_API_KEY` | For AI features | Claude API key |
| `OPENAI_API_KEY` | For AI features | OpenAI API key |

Google OAuth secrets are **not needed** -- preview environments use test mode (auto-login) instead.

If AI secrets are not set, the app will still deploy -- persona creation and conversations just won't generate AI responses.

## Fly App Naming Convention

```
persona-pr-{PR_NUMBER}-be    # Backend
persona-pr-{PR_NUMBER}-fe    # Frontend
persona-pr-{PR_NUMBER}-db    # Postgres (auto-named by fly postgres create)
```

## Preview URL Format

```
Frontend: https://persona-pr-{PR_NUMBER}-fe.fly.dev
Backend:  https://persona-pr-{PR_NUMBER}-be.fly.dev
API docs: https://persona-pr-{PR_NUMBER}-be.fly.dev/docs
```

## Manual Cleanup

If a preview environment gets orphaned (e.g., GitHub Actions fails during teardown), you can clean it up manually:

```bash
fly apps destroy persona-pr-123-be --yes
fly apps destroy persona-pr-123-fe --yes
fly apps destroy persona-pr-123-db --yes  # if postgres app exists separately
```

Or list all preview apps:

```bash
fly apps list | grep persona-pr-
```

## Files Added/Modified

```
.github/workflows/preview-env.yml        # GitHub Actions workflow
backend/seed_preview_data.py             # Sample data seeder for preview DBs
backend/docker-entrypoint.sh             # Modified: runs seed script when ENV=preview
backend/app/routers/auth.py              # Modified: /auth/test-login endpoint
frontend/src/context/AuthContext.tsx      # Modified: auto-login in preview mode
frontend/Dockerfile                      # Modified: NEXT_PUBLIC_PREVIEW_MODE build arg
.gitignore                               # Modified: ignore generated fly.toml files
```

## Limitations

- **Google OAuth**: Bypassed via test mode. Real OAuth login is not available in previews.
- **S3 avatars**: Preview environments don't have AWS credentials, so avatar uploads won't work. DiceBear fallback avatars will be used instead.
- **Cold starts**: If fly.io auto-stops the machines, first request may take 5-10s to wake up
- **Single region**: Preview apps deploy to fly.io's default region (`lhr`), not multi-region
- **No persistent data**: Database is destroyed with the PR. Each push re-creates a fresh DB with seed data.
