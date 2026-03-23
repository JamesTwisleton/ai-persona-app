# Persona Composer

An AI-powered focus group simulator. Create synthetic personas with distinct personalities and watch them debate any topic.

**How it works:** Describe a person in plain English. Claude infers their [OCEAN personality traits](https://en.wikipedia.org/wiki/Big_Five_personality_traits), DALL-E generates a photorealistic avatar, and the system assigns them one of 8 archetypes. Drop multiple personas into a conversation on any topic and let them go.

**Live:** https://personacomposer.app

---

## Contents

- [Local Development](#local-development)
- [Architecture](#architecture)
- [Environment Variables](#environment-variables)
- [AWS Deployment](#aws-deployment)
- [CI/CD — Bitbucket Pipelines](#cicd--bitbucket-pipelines)
- [Development Commands](#development-commands)
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

You need a Google OAuth 2.0 client to handle login.

1. Go to [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials)
2. **Create Credentials → OAuth client ID**
3. Application type: **Web application**
4. Under **Authorised redirect URIs**, add:
   ```
   http://localhost:8000/auth/callback/google
   ```
5. Copy the **Client ID** and **Client Secret** into `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

> **OAuth consent screen:** If prompted, set it to **External**, give the app a name, and add your email as a test user.

### 3. Add API keys

Run the interactive setup script — it opens the right browser tabs and writes keys directly to `backend/.env`:

```bash
./setup-keys.sh
```

Keys needed:
| Key | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |

### 4. Start the app

```bash
docker-compose --profile frontend up
```

Open **http://localhost:3000**.

To rebuild containers after dependency changes:

```bash
docker-compose --profile frontend up --build
```

---

## Architecture

```
┌──────────────────────────┐     ┌──────────────────────────┐
│  Next.js 14 (port 3000)  │────▶│  FastAPI (port 8000)     │
│  TypeScript, Tailwind    │     │  Python 3.11             │
└──────────────────────────┘     └────────────┬─────────────┘
                                               │
                               ┌───────────────┼───────────────┐
                               ▼               ▼               ▼
                        Anthropic API     OpenAI API      PostgreSQL
                        (Claude)          (DALL-E +        (RDS in
                        OCEAN inference   Moderation)       prod)
                        Conversation
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
  → Claude infers 5 OCEAN scores (0.0–1.0)
  → Cosine similarity maps OCEAN vector → 8 archetypes
  → Claude generates a personal motto
  → DALL-E generates a photorealistic headshot
  → Saved to PostgreSQL → 201 Created
```

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
│   │   ├── models/
│   │   │   ├── user.py                      # User + Google OAuth fields
│   │   │   ├── persona.py                   # Persona + OCEAN scores
│   │   │   ├── conversation.py              # Conversation, participants, messages
│   │   │   ├── moderation.py                # ModerationAuditLog
│   │   │   ├── traits.py                    # OCEAN trait system
│   │   │   ├── affinity.py                  # Archetype affinity calculator
│   │   │   └── archetypes.py                # 8 archetype definitions
│   │   ├── routers/
│   │   │   ├── auth.py                      # GET /auth/login, /auth/callback
│   │   │   ├── users.py                     # GET /users/me
│   │   │   ├── personas.py                  # CRUD + /personas/compatibility
│   │   │   ├── conversations.py             # CRUD + POST /continue
│   │   │   └── admin.py                     # Flagged content review
│   │   └── services/
│   │       ├── ocean_inference.py           # Claude → OCEAN scores
│   │       ├── llm_service.py               # Claude → motto + conversation
│   │       ├── image_generation_service.py  # DALL-E → avatar
│   │       ├── content_moderation_service.py
│   │       └── conversation_orchestrator.py
│   ├── tests/                               # 291 tests, 89%+ coverage
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   └── src/
│       ├── app/                             # Next.js App Router pages
│       │   ├── login/                       # Google sign-in
│       │   ├── personas/                    # List + create personas
│       │   ├── p/[id]/                      # Public persona profile
│       │   ├── conversations/               # List + create + view
│       │   └── api/health/                  # Health check endpoint
│       ├── components/
│       │   ├── persona/                     # PersonaCard, OceanBar
│       │   ├── conversation/                # ConversationView, MessageBubble
│       │   ├── auth/                        # AuthGuard
│       │   └── ui/                          # Button, Spinner, ErrorMessage
│       ├── context/AuthContext.tsx          # Global auth state
│       └── lib/                             # api.ts, auth.ts
│
├── terraform/                               # AWS infrastructure (Terraform)
├── docker-compose.yml                       # Local dev orchestration
├── deploy.sh                                # Manual deploy script
├── setup-keys.sh                            # Interactive API key setup
└── bitbucket-pipelines.yml                  # CI/CD pipeline
```

### API docs (local)

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Environment Variables

All variables live in `backend/.env`. Copy from `backend/.env.example` to start.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | Auto-set by Docker Compose for local dev. RDS URL in prod (injected via Secrets Manager). |
| `JWT_SECRET` | ✅ | — | Random secret for signing JWT tokens. Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `GOOGLE_CLIENT_ID` | ✅ | — | Google OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | ✅ | — | Google OAuth 2.0 client secret |
| `GOOGLE_REDIRECT_URI` | ✅ | — | `http://localhost:8000/auth/callback/google` (local) or `https://api.personacomposer.app/auth/callback/google` (prod) |
| `ANTHROPIC_API_KEY` | ✅ | — | Claude API — OCEAN inference, mottos, conversations |
| `OPENAI_API_KEY` | ✅ | — | DALL-E avatar generation + content moderation |
| `TOXICITY_THRESHOLD` | ❌ | `0.7` | Moderation threshold (0.0–1.0). Set to `1.1` to disable. |
| `FRONTEND_URL` | ❌ | `http://localhost:3000` | Used for CORS. Set to `https://personacomposer.app` in prod. |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR` |

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
                                    RDS PostgreSQL (private subnet)

All secrets stored in AWS Secrets Manager (injected at task start)
All images stored in ECR (Elastic Container Registry)
Logs in CloudWatch (/ecs/persona-composer/backend|frontend)
```

### Prerequisites for deployment

- [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.6
- [AWS CLI](https://aws.amazon.com/cli/) configured with credentials
- Docker Desktop running
- An AWS account with a Route53 hosted zone for `personacomposer.app`

### First-time setup

#### 1. Add production redirect URI to Google OAuth

In [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials), edit your OAuth client and add:

```
https://api.personacomposer.app/auth/callback/google
```

under **Authorised redirect URIs**.

#### 2. Configure AWS credentials

Export your IAM credentials:

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

Edit `terraform/terraform.tfvars` and fill in your API keys:

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

This runs three steps in sequence:

1. **`terraform apply`** — provisions VPC, ALB, ECS, RDS, ACM, Route53, ECR, Secrets Manager (~10 minutes, mostly waiting for RDS)
2. **Docker build + ECR push** — builds production images for backend and frontend, pushes to ECR
3. **ECS force redeploy** — triggers rolling deployment of new images

#### Subsequent deploys

After the first run, infrastructure rarely changes. To deploy new code:

```bash
./deploy.sh images    # build + push images only
./deploy.sh redeploy  # force ECS to pull latest images
```

Or both together:

```bash
./deploy.sh images && ./deploy.sh redeploy
```

#### Terraform state

State is stored remotely in S3 (`ai-persona-app-terraform-state-bucket`) with DynamoDB locking (`terraform-state-lock`). Multiple people can run Terraform safely — it will lock the state during apply.

#### Deploy script reference

```bash
./deploy.sh          # Full deploy: infra + images + redeploy
./deploy.sh infra    # Terraform apply only
./deploy.sh images   # Build and push Docker images only
./deploy.sh redeploy # Force ECS services to redeploy
```

### Monitoring

| What | Where |
|---|---|
| ECS services | https://us-east-1.console.aws.amazon.com/ecs/v2/clusters/persona-composer-cluster/services |
| Backend logs | CloudWatch → `/ecs/persona-composer/backend` |
| Frontend logs | CloudWatch → `/ecs/persona-composer/frontend` |
| RDS | https://us-east-1.console.aws.amazon.com/rds/home |
| ALB health | https://us-east-1.console.aws.amazon.com/ec2/home#LoadBalancers |

### Teardown

To destroy all AWS infrastructure:

```bash
cd terraform && terraform destroy
```

> This deletes the RDS instance and all data. The S3 state bucket is preserved.

---

## CI/CD — Bitbucket Pipelines

The pipeline automatically builds and deploys to production on every push to `main`.

### Setup

#### 1. Add repository variables in Bitbucket

Go to your Bitbucket repository → **Repository settings → Pipelines → Repository variables** and add:

| Variable | Value | Secured |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | Yes |
| `AWS_DEFAULT_REGION` | `us-east-1` | No |
| `AWS_ACCOUNT_ID` | `912531404540` | No |

#### 2. Pipeline behaviour

| Branch | What runs |
|---|---|
| Any branch | Backend tests |
| `main` | Tests → build backend image → build frontend image → force ECS redeploy |

Deployments are gated on tests passing. A failed test on `main` will not deploy.

#### 3. IAM permissions for the pipeline user

The `AWS_ACCESS_KEY_ID` used in the pipeline needs these permissions (scope it down from AdministratorAccess after first Terraform run):

- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:InitiateLayerUpload`
- `ecr:UploadLayerPart`
- `ecr:CompleteLayerUpload`
- `ecr:PutImage`
- `ecs:UpdateService`
- `ecs:DescribeServices`

---

## Development Commands

### Local

```bash
# Start all services
docker-compose --profile frontend up

# Rebuild containers (after Dockerfile or requirements changes)
docker-compose --profile frontend up --build

# View live logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart backend (picks up .env changes without rebuild)
docker-compose --profile frontend restart backend

# Wipe database and start fresh
docker-compose --profile frontend down -v && docker-compose --profile frontend up

# Open a shell in the backend container
docker exec -it ai_focus_groups_backend bash
```

### Testing

```bash
# Run all backend tests
docker-compose exec backend pytest -q

# With coverage report (opens at backend/htmlcov/index.html)
docker-compose exec backend pytest --cov=app --cov-report=html

# Single test file
docker-compose exec backend pytest tests/unit/test_ocean_inference_service.py -v
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

The postgres volume has a stale schema. Wipe it:
```bash
docker-compose --profile frontend down -v && docker-compose --profile frontend up
```

---

**`npm ci` lock file error on frontend build**

```bash
cd frontend && npm install && cd ..
docker-compose --profile frontend up --build
```

---

**Content moderation blocking all persona creation**

The OpenAI key is missing or invalid — the service fails safe and blocks everything. Add a valid `OPENAI_API_KEY`, or temporarily disable moderation:
```
TOXICITY_THRESHOLD=1.1
```

---

**OCEAN inference failing**

Check `ANTHROPIC_API_KEY` is set and uncommented in `backend/.env`, then:
```bash
docker-compose --profile frontend restart backend
```

---

**Google OAuth redirect mismatch**

The redirect URI registered in Google Cloud Console must exactly match `GOOGLE_REDIRECT_URI` in your `.env`:

| Environment | Redirect URI |
|---|---|
| Local | `http://localhost:8000/auth/callback/google` |
| Production | `https://api.personacomposer.app/auth/callback/google` |

Both must be registered in your Google OAuth client's **Authorised redirect URIs** list.

---

**ECS tasks failing to start (production)**

Check CloudWatch logs:
```bash
aws logs tail /ecs/persona-composer/backend --follow
aws logs tail /ecs/persona-composer/frontend --follow
```

Common causes: ECR image not pushed yet, Secrets Manager permissions, RDS not reachable (check security groups).

---

**Terraform state lock stuck**

If a previous `terraform apply` was interrupted:
```bash
cd terraform && terraform force-unlock <lock-id>
```

Get the lock ID from the error message.
