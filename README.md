# Persona Composer

An AI-powered focus group simulator. Create synthetic personas with distinct personalities, watch them debate any topic, and share your experiments with the world.

**How it works:** Describe a person in plain English. Claude infers their [OCEAN personality traits](https://en.wikipedia.org/wiki/Big_Five_personality_traits), DALL-E generates a photorealistic avatar, and the system assigns them one of 8 archetypes. Drop multiple personas into a conversation on any topic and let them go.

**Live:** https://personacomposer.app

---

## Contents

- [Local Development](#local-development)
- [Features](#features)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Environment Variables](#environment-variables)
- [AWS Deployment](#aws-deployment)
- [CI/CD — GitHub Actions](#cicd--github-actions)
- [Development Commands](#development-commands)
- [Smoke Tests](#smoke-tests)
- [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running)
- A Google account (for OAuth login)
- API keys for [Anthropic](https://console.anthropic.com/settings/keys) and [OpenAI](https://platform.openai.com/api-keys)

### 1. Clone and create your env file

```bash
git clone <repo-url>
cd ai-persona-app
cp backend/.env.example backend/.env
```

### 2. Google OAuth setup (~5 minutes)

1. Go to [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials)
2. **Create Credentials → OAuth client ID**
3. Application type: **Web application**
4. Under **Authorised redirect URIs**, add:
   ```
   http://localhost:8000/auth/callback/google
   ```
5. Copy **Client ID** and **Client Secret** into `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

> **OAuth consent screen:** If prompted, set it to **External**, give the app a name, and add your email as a test user.

### 3. Add API keys

```bash
./setup-keys.sh
```

This opens the right browser tabs and writes keys directly to `backend/.env`.

| Key | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |

### 4. Avatar storage (local)

By default, generated avatars are saved to disk under `./local_avatars/` and served by the backend at `http://localhost:8000/avatars/<filename>`. No S3 credentials needed for local dev.

Add to `backend/.env`:

```
LOCAL_AVATAR_DIR=./local_avatars
```

To use S3 instead, leave `LOCAL_AVATAR_DIR` blank and set `S3_AVATAR_BUCKET` (see [Environment Variables](#environment-variables)).

### 5. Start the app

```bash
docker-compose up
```

Open **http://localhost:3000**.

To rebuild after dependency or Dockerfile changes:

```bash
docker-compose up --build
```

---

## Features

### Core

| Feature | Description |
|---|---|
| **Google OAuth** | Sign in with Google — no passwords |
| **Persona creation** | Describe a person → Claude infers OCEAN traits → DALL-E generates avatar |
| **OCEAN model** | Big Five personality scoring (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) |
| **8 archetypes** | Analyst, Socialite, Innovator, Activist, Pragmatist, Traditionalist, Skeptic, Optimist |
| **Focus groups** | Drop 1–N personas into a conversation topic and generate multi-turn discussion |
| **Content moderation** | OpenAI Moderation API screens persona descriptions and messages |

### Social / Discovery

| Feature | Description |
|---|---|
| **Public feed** | Home page shows all public personas and conversations sorted by Hot / Top / New |
| **Hot score** | `(upvotes + log10(views+1)) / (age_hours+2)^1.5` — surfaces trending content |
| **Upvoting** | Any logged-in user can upvote any public persona or conversation (toggle) |
| **Page view tracking** | Deduplicated per user (or IP) per day — no spam inflation |
| **Public / private** | Toggle when creating a persona or conversation — private content is invisible to others |
| **Visibility patch** | Change public/private at any time via the API |
| **Conversation forking** | Fork any public conversation — inherits full message history, continue independently |
| **Cascade delete** | Deleting a persona also deletes all conversations it participated in |
| **Superuser** | Site owner (`ajtwisleton@gmail.com`) can delete any persona or conversation |

### Planned

- Redis caching for the discovery feed
- Email notifications for upvote milestones
- Persona compatibility comparison page

---

## Architecture

### System diagram

```
┌──────────────────────────┐     ┌──────────────────────────┐
│  Next.js 14 (port 3000)  │────▶│  FastAPI (port 8000)     │
│  TypeScript, Tailwind    │     │  Python 3.11             │
└──────────────────────────┘     └────────────┬─────────────┘
                                               │
                               ┌───────────────┼───────────────┐
                               ▼               ▼               ▼
                        Anthropic API     OpenAI API      PostgreSQL
                        (Claude)          (DALL-E +        (Docker /
                        OCEAN inference   Moderation)       RDS in prod)
                        Mottos
                        Conversations
```

### URLs

| Environment | Frontend | Backend API |
|---|---|---|
| Local | http://localhost:3000 | http://localhost:8000 |
| Production | https://personacomposer.app | https://api.personacomposer.app |

### Persona creation pipeline

```
POST /personas (your description)
  → Content moderation check (OpenAI)
  → Claude infers 5 OCEAN scores [0.0–1.0]
  → Cosine similarity maps OCEAN vector → 8 archetypes
  → Claude generates a personal motto
  → DALL-E generates a photorealistic headshot
  → Saved to PostgreSQL → 201 Created
```

### Hot score formula

The discovery feed uses a time-decayed engagement score:

```
hot_score = (upvotes + log10(views + 1)) / (age_hours + 2) ^ 1.5
```

- Content peaks quickly and decays over time
- Views count less than upvotes (`log10` dampening)
- The `+2` in the denominator prevents new content from getting infinite scores

### OCEAN personality model

| Trait | Low | High |
|---|---|---|
| **O**penness | Conventional | Imaginative |
| **C**onscientiousness | Spontaneous | Organised |
| **E**xtraversion | Introverted | Outgoing |
| **A**greeableness | Sceptical | Trusting |
| **N**euroticism | Calm | Anxious |

### 8 archetypes

| Archetype | Core traits |
|---|---|
| Analyst | High C, Low E, Low A |
| Socialite | High E, High A, Low C |
| Innovator | High O, Moderate E |
| Activist | High O, High A, High E |
| Pragmatist | Balanced, Low N |
| Traditionalist | Low O, High C, High A |
| Skeptic | High O, Low A, Low E |
| Optimist | High E, High A, High O |

### Project structure

```
ai-persona-app/
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI entry point
│   │   ├── config.py                        # Settings from .env (Pydantic)
│   │   ├── auth.py                          # JWT utilities + OAuth setup
│   │   ├── dependencies.py                  # get_current_user, get_optional_user
│   │   ├── models/
│   │   │   ├── user.py                      # User + Google OAuth fields + is_superuser
│   │   │   ├── persona.py                   # Persona + OCEAN + is_public + view/upvote counts
│   │   │   ├── conversation.py              # Conversation + forked_from_id + social fields
│   │   │   ├── social.py                    # Upvote, PageView models
│   │   │   ├── moderation.py                # ModerationAuditLog
│   │   │   ├── traits.py                    # OCEAN trait system
│   │   │   ├── affinity.py                  # Archetype affinity calculator
│   │   │   └── archetypes.py                # 8 archetype definitions
│   │   ├── routers/
│   │   │   ├── auth.py                      # GET /auth/login, /auth/callback
│   │   │   ├── users.py                     # GET /users/me
│   │   │   ├── personas.py                  # CRUD + /personas/compatibility
│   │   │   ├── conversations.py             # CRUD + POST /continue
│   │   │   ├── discovery.py                 # Public feed, upvotes, views, fork
│   │   │   └── admin.py                     # Flagged content review
│   │   └── services/
│   │       ├── ocean_inference.py           # Claude → OCEAN scores
│   │       ├── llm_service.py               # Claude → motto + conversation turns
│   │       ├── image_generation_service.py  # DALL-E → avatar
│   │       ├── content_moderation_service.py
│   │       └── conversation_orchestrator.py
│   ├── tests/                               # 355 tests, 87%+ coverage
│   ├── docker-entrypoint.sh                 # Runs DB init + idempotent ALTER TABLE migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   └── src/
│       ├── app/                             # Next.js App Router pages
│       │   ├── page.tsx                     # Home — public discovery feed
│       │   ├── login/                       # Google sign-in
│       │   ├── personas/                    # List + create personas
│       │   ├── p/[id]/                      # Public persona profile + upvote
│       │   ├── c/[id]/                      # Public conversation + upvote + fork
│       │   ├── conversations/               # Authenticated list + create + continue
│       │   └── api/health/                  # Health check
│       ├── components/
│       │   ├── persona/                     # PersonaCard, OceanBar
│       │   ├── conversation/                # ConversationView, MessageBubble
│       │   ├── social/                      # UpvoteButton, ForkModal
│       │   ├── auth/                        # AuthGuard
│       │   └── ui/                          # Button, Spinner, ErrorMessage
│       ├── context/AuthContext.tsx          # Global auth state
│       ├── types/index.ts                   # All TypeScript types
│       └── lib/                             # api.ts, auth.ts
│
├── terraform/                               # AWS infrastructure (Terraform)
├── .github/workflows/                       # GitHub Actions CI/CD
│   ├── python-ci.yml                        # Backend tests + deploy on push to main
│   ├── nextjs-ci.yml                        # Frontend build + deploy on push to main
│   ├── python-docker-ecr-ecs.yml            # Manual backend redeploy
│   └── nextjs-docker-ecr-ecs.yml           # Manual frontend redeploy
├── docker-compose.yml                       # Local dev orchestration
├── deploy.sh                                # Manual deploy script
└── setup-keys.sh                            # Interactive API key setup
```

---

## API Reference

### Authentication

All protected endpoints require a JWT Bearer token:

```
Authorization: Bearer <token>
```

Obtain a token by signing in via `GET /auth/login/google`. The token is valid for 24 hours.

Interactive docs (local): **http://localhost:8000/docs**

### Endpoints

#### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/auth/login/google` | — | Redirect to Google sign-in |
| GET | `/auth/callback/google` | — | OAuth callback → JWT → redirect to frontend |

#### Users

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users/me` | ✅ | Current user profile |

#### Personas

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/personas` | ✅ | Create persona (OCEAN inference + avatar) |
| GET | `/personas` | ✅ | List your personas |
| GET | `/personas/{id}` | ✅ | Get your persona by unique ID |
| DELETE | `/personas/{id}` | ✅ | Delete your persona (cascades to conversations) |
| POST | `/personas/compatibility` | ✅ | OCEAN compatibility analysis between personas |
| GET | `/archetypes` | — | List all 8 archetypes |

**Create persona request body:**
```json
{
  "name": "Alice",
  "age": 35,
  "gender": "Female",
  "description": "A pragmatic data scientist who values evidence over gut feel...",
  "attitude": "Neutral",
  "is_public": true
}
```

#### Conversations

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/conversations` | ✅ | Create a focus group conversation |
| GET | `/conversations` | ✅ | List your conversations |
| GET | `/conversations/{id}` | ✅ | Get conversation with all messages |
| POST | `/conversations/{id}/continue` | ✅ | Generate the next turn |

**Create conversation request body:**
```json
{
  "topic": "Should we colonize Mars?",
  "persona_ids": ["abc123", "xyz789"],
  "is_public": true
}
```

#### Discovery (public feed)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/discover` | — | Public feed — `?sort=hot\|top\|new` |
| GET | `/p/{id}` | Optional | Public persona profile (tracks view) |
| GET | `/c/{id}` | Optional | Public conversation (tracks view) |
| POST | `/p/{id}/upvote` | ✅ | Toggle upvote on a persona |
| POST | `/c/{id}/upvote` | ✅ | Toggle upvote on a conversation |
| PATCH | `/personas/{id}/visibility` | ✅ | Set `is_public` on your persona |
| PATCH | `/conversations/{id}/visibility` | ✅ | Set `is_public` on your conversation |
| POST | `/conversations/{id}/fork` | ✅ | Fork a conversation (inherits message history) |
| DELETE | `/personas/{id}/force` | ✅ Superuser | Delete any persona |
| DELETE | `/conversations/{id}/force` | ✅ Superuser | Delete any conversation |

**Discover query params:**

| Param | Values | Default | Description |
|---|---|---|---|
| `sort` | `hot`, `top`, `new` | `hot` | Sort algorithm |
| `limit` | 1–50 | 20 | Results per type (personas + conversations separately) |

**Fork request body:**
```json
{
  "topic": "Optional new topic — defaults to original",
  "persona_ids": ["abc123"]
}
```
If `persona_ids` is omitted, the fork inherits the original participants. If provided, they must be personas you own.

**Visibility request body:**
```json
{ "is_public": false }
```

#### Admin

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/admin/flagged` | ✅ Admin | List flagged content for review |

---

## Environment Variables

All variables live in `backend/.env`. Copy from `backend/.env.example` to start.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | Auto-set by Docker Compose for local. RDS URL in prod (injected via Secrets Manager). |
| `JWT_SECRET` | ✅ | — | Secret for JWT signing. Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `GOOGLE_CLIENT_ID` | ✅ | — | Google OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | ✅ | — | Google OAuth 2.0 client secret |
| `GOOGLE_REDIRECT_URI` | ✅ | — | `http://localhost:8000/auth/callback/google` (local) or `https://api.personacomposer.app/auth/callback/google` (prod) |
| `ANTHROPIC_API_KEY` | ✅ | — | Claude API — OCEAN inference, mottos, conversations |
| `OPENAI_API_KEY` | ✅ | — | DALL-E avatar generation + content moderation |
| `LOCAL_AVATAR_DIR` | ❌ | — | Path to store avatars locally (e.g. `./local_avatars`). Takes priority over S3. Served at `/avatars/<filename>`. |
| `BACKEND_URL` | ❌ | `http://localhost:8000` | Base URL of the backend — used to construct local avatar URLs. |
| `S3_AVATAR_BUCKET` | ❌ | — | S3 bucket name for avatar storage (production). Leave blank when using `LOCAL_AVATAR_DIR`. |
| `AWS_DEFAULT_REGION` | ❌ | `eu-west-1` | AWS region for S3. Only needed when `S3_AVATAR_BUCKET` is set. |
| `TOXICITY_THRESHOLD` | ❌ | `0.7` | Moderation sensitivity (0.0–1.0). Set `1.1` to disable. |
| `FRONTEND_URL` | ❌ | `http://localhost:3000` | CORS origin. Set to `https://personacomposer.app` in prod. |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR` |

---

## Database Migrations

The app uses a simple `ALTER TABLE IF NOT EXISTS` migration system run by `docker-entrypoint.sh` on every container start. This is safe to run multiple times — it only adds columns that don't already exist.

New columns added automatically at startup:

| Table | Column | Default |
|---|---|---|
| `personas` | `is_public` | `TRUE` |
| `personas` | `view_count` | `0` |
| `personas` | `upvote_count` | `0` |
| `conversations` | `is_public` | `TRUE` |
| `conversations` | `forked_from_id` | `NULL` |
| `conversations` | `view_count` | `0` |
| `conversations` | `upvote_count` | `0` |
| `users` | `is_superuser` | `FALSE` |

Two new tables are created on first run:
- **`upvotes`** — one row per user per target, unique constraint enforces toggle semantics
- **`page_views`** — one row per user (or IP hash) per target per day, deduplicates view counts

The superuser seed (`ajtwisleton@gmail.com`) is applied on every startup via `UPDATE ... WHERE email = ...` — idempotent.

---

## AWS Deployment

The production stack runs on AWS ECS Fargate with RDS PostgreSQL and an Application Load Balancer. Terraform manages all infrastructure.

### Production architecture

```
Internet
    │
    ▼
Route53 (personacomposer.app)
    │
    ▼
ACM (TLS certificate)
    │
    ▼
ALB (Application Load Balancer)
    ├── personacomposer.app         → Frontend ECS service (port 3000)
    └── api.personacomposer.app     → Backend ECS service  (port 8000)
                                              │
                                              ▼
                                    RDS PostgreSQL 15 (private subnet)

All secrets in AWS Secrets Manager (injected at ECS task start)
All images in ECR (Elastic Container Registry)
Logs in CloudWatch (/ecs/persona-composer/backend|frontend)
```

### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.6
- [AWS CLI](https://aws.amazon.com/cli/) configured
- Docker Desktop running
- Route53 hosted zone for `personacomposer.app`

### First-time setup

#### 1. Add production redirect URI to Google OAuth

In [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials), add to **Authorised redirect URIs**:

```
https://api.personacomposer.app/auth/callback/google
```

#### 2. Configure AWS credentials

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

The IAM user needs **AdministratorAccess** for the initial Terraform run.

#### 3. Create the Terraform variables file

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Edit `terraform/terraform.tfvars`:

```hcl
anthropic_api_key    = "sk-ant-..."
openai_api_key       = "sk-proj-..."
jwt_secret           = "your-jwt-secret"
google_client_id     = "your-client-id.apps.googleusercontent.com"
google_client_secret = "GOCSPX-..."
```

> `terraform.tfvars` is git-ignored. Never commit it.

#### 4. Deploy

```bash
./deploy.sh
```

This runs three steps:

1. **`terraform apply`** — provisions VPC, ALB, ECS, RDS, ACM, Route53, ECR, Secrets Manager (~10 min)
2. **Docker build + ECR push** — builds production images for backend and frontend
3. **ECS force redeploy** — rolling deployment of new images, waits for stability

#### Subsequent deploys

```bash
./deploy.sh images    # build + push images only
./deploy.sh redeploy  # force ECS to pull latest images
./deploy.sh images && ./deploy.sh redeploy  # code deploy
```

#### Deploy script reference

```bash
./deploy.sh          # Full: infra + images + redeploy
./deploy.sh infra    # Terraform apply only
./deploy.sh images   # Build and push Docker images only
./deploy.sh redeploy # Force ECS services to redeploy
```

#### Terraform state

State is stored in S3 (`ai-persona-app-terraform-state-bucket`) with DynamoDB locking (`terraform-state-lock`).

### Monitoring

| What | Where |
|---|---|
| ECS services | https://us-east-1.console.aws.amazon.com/ecs/v2/clusters/persona-composer-cluster/services |
| Backend logs | CloudWatch → `/ecs/persona-composer/backend` |
| Frontend logs | CloudWatch → `/ecs/persona-composer/frontend` |
| RDS | https://us-east-1.console.aws.amazon.com/rds/home |
| ALB health | https://us-east-1.console.aws.amazon.com/ec2/home#LoadBalancers |

### Teardown

```bash
cd terraform && terraform destroy
```

> This deletes the RDS instance and all data. The S3 state bucket is preserved.

---

## CI/CD — GitHub Actions

### Behaviour

| Trigger | What runs |
|---|---|
| Any PR | Backend tests + frontend build |
| Push to `main` | Tests → build + push images to ECR → ECS rolling deploy → wait for stability → smoke test |
| Manual (`workflow_dispatch`) | Emergency redeploy (skips tests) |

The deploy job only runs after tests pass. After `aws ecs update-service`, the workflow blocks on `aws ecs wait services-stable` until new tasks are healthy and old tasks are deprovisioned — the workflow fails if this takes more than 10 minutes. A final curl smoke test confirms the live endpoint is responding before the job is marked green.

### Setup

Go to **GitHub → Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |

### Required IAM permissions

```
ecr:GetAuthorizationToken
ecr:BatchCheckLayerAvailability
ecr:InitiateLayerUpload / UploadLayerPart / CompleteLayerUpload / PutImage
ecs:UpdateService
ecs:DescribeServices
ecs:DescribeTasks
```

---

## Development Commands

### Local

```bash
# Start all services (db + backend + frontend)
docker-compose up

# Rebuild after Dockerfile or dependency changes
docker-compose up --build

# View live logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart backend (picks up .env changes without rebuild)
docker-compose restart backend

# Wipe database and start fresh
docker-compose down -v && docker-compose up

# Shell in backend container
docker exec -it ai_focus_groups_backend bash
```

### Testing

```bash
# Run all backend tests
docker-compose exec backend pytest -q

# With coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Single test file
docker-compose exec backend pytest tests/unit/test_ocean_inference_service.py -v
```

---

## Smoke Tests

End-to-end smoke tests using [Playwright](https://playwright.dev/) that verify core functionality (homepage, auth pages, API health, admin, social features, etc.).

### Prerequisites

```bash
cd smoke-tests
npm install
npx playwright install chromium
```

### Run against local

Make sure both the frontend (port 3000) and backend (port 8000) are running (`docker-compose up`), then:

```bash
cd smoke-tests
SMOKE_TEST_BASE_URL=http://localhost:3000 SMOKE_TEST_API_URL=http://localhost:8000 npx playwright test
```

### Run against production

```bash
cd smoke-tests
npx playwright test
```

This uses the default URLs (`https://personacomposer.app` / `https://api.personacomposer.app`).

### Headed mode (watch the browser)

```bash
SMOKE_TEST_BASE_URL=http://localhost:3000 SMOKE_TEST_API_URL=http://localhost:8000 npx playwright test --headed
```

### View the HTML report

```bash
npx playwright show-report
```

---

## Troubleshooting

**Docker daemon not running**
```
Cannot connect to the Docker daemon
```
Open Docker Desktop and wait for it to fully start.

---

**Database schema errors** (e.g. `column users.is_admin does not exist`)

Wipe the stale postgres volume:
```bash
docker-compose down -v && docker-compose up
```

---

**`npm ci` lock file error on frontend build**

```bash
cd frontend && npm install && cd ..
docker-compose up --build
```

---

**Content moderation blocking all persona creation**

The OpenAI key is missing or invalid. Add a valid `OPENAI_API_KEY`, or disable moderation:
```
TOXICITY_THRESHOLD=1.1
```

---

**OCEAN inference failing**

Check `ANTHROPIC_API_KEY` is set in `backend/.env`, then:
```bash
docker-compose restart backend
```

---

**Google OAuth Error 400: redirect_uri_mismatch**

The redirect URI in Google Cloud Console must exactly match `GOOGLE_REDIRECT_URI` in `.env`:

| Environment | Redirect URI |
|---|---|
| Local | `http://localhost:8000/auth/callback/google` |
| Production | `https://api.personacomposer.app/auth/callback/google` |

Both must be listed in your OAuth client's **Authorised redirect URIs**.

---

**Google OAuth Error 400: invalid_state (production)**

This was caused by custom in-memory state storage that doesn't survive across multiple ECS task instances. Fixed in commit `5713b96` — authlib now manages CSRF state entirely via the Starlette session cookie (signed with `JWT_SECRET`).

---

**ECS tasks failing to start**

```bash
aws logs tail /ecs/persona-composer/backend --follow
aws logs tail /ecs/persona-composer/frontend --follow
```

Common causes: ECR image not pushed, Secrets Manager permissions missing, RDS security group not allowing ECS.

---

**Terraform state lock stuck**

```bash
cd terraform && terraform force-unlock <lock-id>
```

Get the lock ID from the error message.
