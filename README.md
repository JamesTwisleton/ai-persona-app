# Persona Composer

An AI-powered focus group simulator. Create synthetic personas with distinct personalities and watch them debate any topic.

**How it works:** You describe a person in plain English. The app uses Claude to infer their [OCEAN personality traits](https://en.wikipedia.org/wiki/Big_Five_personality_traits), generates a photorealistic avatar via DALL-E, and assigns them to one of 8 archetypes. Then you drop multiple personas into a conversation and let them go.

---

## Quick Start

### 1. Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running)
- A Google account (for OAuth login)
- API keys for [Anthropic](https://console.anthropic.com/settings/keys) and [OpenAI](https://platform.openai.com/api-keys)

### 2. Clone and configure

```bash
git clone <repo-url>
cd ai-persona-app
cp backend/.env.example backend/.env
```

### 3. Set up Google OAuth

You need a Google OAuth app to handle login. This takes ~5 minutes:

1. Go to [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Web application**
4. Add authorised redirect URI: `http://localhost:8000/auth/callback/google`
5. Copy the **Client ID** and **Client Secret** into `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

> If prompted to configure an OAuth consent screen first, set it to **External**, fill in the app name, and add your own email as a test user.

### 4. Add API keys

Run the setup script — it opens the right browser tabs and writes your keys directly to `.env`:

```bash
./setup-keys.sh
```

### 5. Run

```bash
docker-compose --profile frontend up
```

Open **http://localhost:3000** in your browser.

---

## What You'll See

| Screen | URL | Description |
|---|---|---|
| Login | `/login` | Sign in with Google |
| Personas | `/personas` | Your persona library |
| Create Persona | `/personas/new` | Describe someone, AI builds them |
| Persona Profile | `/p/{id}` | Public shareable persona page |
| Conversations | `/conversations` | Your focus group sessions |
| New Conversation | `/conversations/new` | Pick personas + topic |
| Conversation View | `/conversations/{id}` | Watch them talk, continue turns |

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Next.js 14    │────▶│  FastAPI (8000) │────▶│  PostgreSQL      │
│   (port 3000)   │     │  Python 3.11    │     │  (port 5432)     │
└─────────────────┘     └────────┬────────┘     └──────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
             Anthropic API    OpenAI API    OpenAI API
             (Claude)         (DALL-E)      (Moderation)
             OCEAN inference  Avatars       Content safety
             Conversation
```

### Persona Creation Pipeline

When you submit a description, the backend runs this pipeline:

```
Your description
  → Content moderation check
  → Claude infers 5 OCEAN personality scores (0.0–1.0)
  → Cosine similarity maps OCEAN vector to 8 archetypes
  → Claude generates a personal motto
  → DALL-E generates a photorealistic avatar
  → Saved to database → 201 Created
```

### OCEAN Personality Model

Personas are scored on the [Big Five](https://en.wikipedia.org/wiki/Big_Five_personality_traits):

| Trait | Low | High |
|---|---|---|
| **O**penness | Conventional | Imaginative |
| **C**onscientiousness | Spontaneous | Organised |
| **E**xtraversion | Introverted | Outgoing |
| **A**greeableness | Sceptical | Trusting |
| **N**euroticism | Calm | Anxious |

These scores position each persona in a 5D vector space, ensuring genuine diversity when you build a focus group.

### 8 Archetypes

| Archetype | Core Traits |
|---|---|
| Analyst | High C, Low E, Low A |
| Socialite | High E, High A, Low C |
| Innovator | High O, Moderate E |
| Activist | High O, High A, High E |
| Pragmatist | Balanced, Low N |
| Traditionalist | Low O, High C, High A |
| Skeptic | High O, Low A, Low E |
| Optimist | High E, High A, High O |

---

## Environment Variables

All variables live in `backend/.env`. Copy from `backend/.env.example` to start.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Auto-set by Docker Compose — don't change for local dev |
| `JWT_SECRET` | ✅ | Random secret for JWT signing |
| `GOOGLE_CLIENT_ID` | ✅ | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | ✅ | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | ✅ | `http://localhost:8000/auth/callback/google` |
| `ANTHROPIC_API_KEY` | ✅ | Claude API — OCEAN inference, mottos, conversation |
| `OPENAI_API_KEY` | ✅ | DALL-E avatars + content moderation |
| `TOXICITY_THRESHOLD` | ❌ | Default `0.7`. Set to `1.1` to disable moderation |
| `FRONTEND_URL` | ❌ | Default `http://localhost:3000` |
| `LOG_LEVEL` | ❌ | Default `INFO` |

---

## Development

### Useful commands

```bash
# View live logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart backend (picks up .env changes)
docker-compose --profile frontend restart backend

# Rebuild containers (after changing requirements.txt or Dockerfile)
docker-compose --profile frontend up --build

# Open a shell in the backend container
docker exec -it ai_focus_groups_backend bash

# Wipe the database and start fresh
docker-compose --profile frontend down -v && docker-compose --profile frontend up
```

### Running tests

```bash
# All tests
docker-compose exec backend pytest -q

# With coverage report
docker-compose exec backend pytest --cov=app --cov-report=html

# Single file
docker-compose exec backend pytest tests/unit/test_ocean_inference_service.py -v
```

### Project structure

```
ai-persona-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings (loaded from .env via Pydantic)
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # User + Google OAuth fields
│   │   │   ├── persona.py       # Persona + OCEAN scores
│   │   │   ├── conversation.py  # Conversation, participants, messages
│   │   │   ├── moderation.py    # ModerationAuditLog
│   │   │   ├── traits.py        # OCEAN trait system + TraitRegistry
│   │   │   ├── affinity.py      # Archetype affinity calculator
│   │   │   └── archetypes.py    # 8 archetype definitions
│   │   ├── routers/             # API endpoints
│   │   │   ├── auth.py          # GET /auth/login, GET /auth/callback
│   │   │   ├── users.py         # GET /users/me
│   │   │   ├── personas.py      # CRUD + compatibility analysis
│   │   │   ├── conversations.py # CRUD + POST /continue
│   │   │   └── admin.py         # Flagged content review (admin only)
│   │   └── services/
│   │       ├── ocean_inference.py          # Claude → OCEAN scores
│   │       ├── llm_service.py              # Claude → motto + conversation
│   │       ├── image_generation_service.py # DALL-E → avatar (DiceBear fallback)
│   │       ├── content_moderation_service.py # OpenAI moderation API
│   │       ├── conversation_orchestrator.py  # Drives turn generation
│   │       └── prompt_templates.py           # LLM prompt templates
│   └── tests/                   # 291 tests, 89%+ coverage
│
├── frontend/
│   └── src/
│       ├── app/                 # Next.js App Router pages
│       ├── components/
│       │   ├── persona/         # PersonaCard, OceanBar (trait visualisation)
│       │   ├── conversation/    # ConversationView, MessageBubble
│       │   ├── auth/            # AuthGuard (protected route wrapper)
│       │   ├── layout/          # Navbar
│       │   └── ui/              # Button, Spinner, ErrorMessage
│       ├── context/             # AuthContext (global auth state)
│       ├── lib/                 # api.ts (fetch wrapper), auth.ts (token helpers)
│       └── types/               # TypeScript types for Persona, Conversation, User
│
├── docker-compose.yml
├── setup-keys.sh                # Interactive API key setup script
└── backend/.env.example         # Environment variable template
```

### API docs

With the app running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Troubleshooting

**Docker daemon not running**
```
Cannot connect to the Docker daemon
```
Open Docker Desktop and wait for it to fully start before running docker-compose.

---

**Database schema errors (e.g. `column users.is_admin does not exist`)**

The database volume has a stale schema from a previous run. Wipe it and restart:
```bash
docker-compose --profile frontend down -v && docker-compose --profile frontend up
```

---

**`npm ci` lock file error during frontend build**

Regenerate the lock file then rebuild:
```bash
cd frontend && npm install && cd ..
docker-compose --profile frontend up --build
```

---

**Content moderation blocking all persona creation**

The OpenAI key is missing or invalid, causing fail-safe mode (blocks everything). Either add a valid `OPENAI_API_KEY` to `backend/.env`, or temporarily disable moderation:
```
TOXICITY_THRESHOLD=1.1
```

---

**OCEAN inference failing**

Check `ANTHROPIC_API_KEY` is set and not commented out in `backend/.env`, then restart:
```bash
docker-compose --profile frontend restart backend
```

---

**Google OAuth redirect mismatch**

The redirect URI in Google Cloud Console must exactly match `GOOGLE_REDIRECT_URI` in your `.env`. For local dev:
```
http://localhost:8000/auth/callback/google
```
