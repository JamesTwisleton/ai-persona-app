# AI Focus Groups - Project Status

**Last Updated:** 2026-03-19
**Current Phase:** Phase 7 Complete — Conversation System
**Overall Progress:** 70% Complete

---

## 🎯 Quick Overview

AI Focus Groups is a platform for creating AI-powered personas and simulating focus group conversations. The system uses the scientifically-validated OCEAN (Big Five) personality model to generate psychologically realistic personas that can discuss any topic.

**Unique Innovation:** Users describe personas naturally (name, age, occupation, backstory), and Claude AI infers their OCEAN personality traits. The system then calculates archetype affinities and generates context-aware conversation responses.

---

## 📊 Current Status

### Completed Phases ✅

#### Phase 1: Infrastructure & Scaffolding (100%)
- ✅ Docker Compose environment (FastAPI, PostgreSQL, Next.js)
- ✅ Testing infrastructure (pytest, coverage reporting)
- ✅ Environment configuration

#### Phase 2: Core Backend Services (100%)
- ✅ **Google OAuth 2.0** authentication
- ✅ **JWT tokens** (access + refresh)
- ✅ User model with OAuth integration
- ✅ Protected API endpoints
- ✅ **28 passing tests** (85%+ coverage)
- ✅ Swagger UI documentation

#### Phase 3A: OCEAN Personality System (100%)
- ✅ **Trait system** (OCEAN + extensible architecture)
- ✅ **PersonalityVector** (5D vector with Euclidean distance)
- ✅ **AffinityCalculator** (cosine similarity + temperature softmax)
- ✅ **8 archetypes** (Analyst, Socialite, Innovator, Activist, Pragmatist, Traditionalist, Skeptic, Optimist)
- ✅ **53 passing tests** (95%+ coverage)
- ✅ Scientific validation (OCEAN is gold standard in psychology)

**Files:**
- [`backend/app/models/traits.py`](backend/app/models/traits.py) - Trait system
- [`backend/app/models/affinity.py`](backend/app/models/affinity.py) - Affinity calculator
- [`backend/app/models/archetypes.py`](backend/app/models/archetypes.py) - 8 archetypes

#### Phase 3B: Database & OCEAN Inference (100%)
- ✅ Persona model with OCEAN columns in database
- ✅ **OceanInferenceService** — Claude API integration for OCEAN inference from backstory
- ✅ **POST /personas** — Full creation pipeline (moderation → OCEAN → affinities → save)
- ✅ **GET /personas**, **GET /personas/{id}**, **DELETE /personas/{id}**
- ✅ **POST /personas/compatibility** — Pairwise Euclidean distance + diversity score
- ✅ **GET /archetypes** — List all personality archetypes

**Files:**
- [`backend/app/models/persona.py`](backend/app/models/persona.py) - Persona model
- [`backend/app/services/ocean_inference.py`](backend/app/services/ocean_inference.py) - OCEAN inference
- [`backend/app/routers/personas.py`](backend/app/routers/personas.py) - Persona endpoints

#### Phase 4: AI Integration — LLM & Image Generation (100%)
- ✅ **LLMService** — Claude Haiku for motto generation and conversation responses
- ✅ **ImageGenerationService** — DALL-E avatar generation with DiceBear fallback
- ✅ **PromptTemplates** — MottoPromptTemplate, ConversationPromptTemplate
- ✅ Persona motto auto-generated on creation (non-blocking on failure)
- ✅ Avatar URL auto-generated on creation (non-blocking on failure)
- ✅ All AI services use injectable client pattern for testability

**Files:**
- [`backend/app/services/llm_service.py`](backend/app/services/llm_service.py) - LLM service
- [`backend/app/services/image_generation_service.py`](backend/app/services/image_generation_service.py) - Image generation
- [`backend/app/services/prompt_templates.py`](backend/app/services/prompt_templates.py) - Prompt templates

#### Phase 5: Content Moderation (100%)
- ✅ **ContentModerationService** — OpenAI Moderation API integration
- ✅ Fails safe (returns score=1.0) on API error — blocks content when uncertain
- ✅ Fail-open on service outage — persona creation proceeds if moderation is unavailable
- ✅ **ModerationAuditLog** model — audit trail for blocked/flagged content
- ✅ **is_admin** field on User model
- ✅ **GET /admin/flagged-content** — admin review queue
- ✅ **POST /admin/approve/{id}**, **POST /admin/block/{id}** — admin actions
- ✅ Audit log written when persona description is blocked or conversation message is flagged

**Files:**
- [`backend/app/services/content_moderation_service.py`](backend/app/services/content_moderation_service.py) - Moderation service
- [`backend/app/models/moderation.py`](backend/app/models/moderation.py) - Audit log model
- [`backend/app/routers/admin.py`](backend/app/routers/admin.py) - Admin endpoints

#### Phase 7: Conversation System (100%)
- ✅ **Conversation model** — topic, turn_count, max_turns, is_complete property
- ✅ **ConversationParticipant** — links personas to conversations
- ✅ **ConversationMessage** — per-turn messages with toxicity scores and moderation status
- ✅ **ConversationOrchestrator** — generates one turn per persona with moderation + regeneration
- ✅ Toxic messages regenerated up to 2 times; saved as "flagged" if still toxic
- ✅ **POST /conversations** — create with persona list
- ✅ **GET /conversations** — list user's conversations
- ✅ **GET /conversations/{id}** — conversation details with messages
- ✅ **POST /conversations/{id}/continue** — generate next turn

**Files:**
- [`backend/app/models/conversation.py`](backend/app/models/conversation.py) - Conversation models
- [`backend/app/services/conversation_orchestrator.py`](backend/app/services/conversation_orchestrator.py) - Orchestrator
- [`backend/app/routers/conversations.py`](backend/app/routers/conversations.py) - Conversation endpoints

---

### Pending Phases ⏳

#### Phase 6: Frontend Development (0%)
- [ ] Next.js frontend setup
- [ ] Personality grid visualization
- [ ] Persona profile pages
- [ ] Conversation UI

#### Phase 8-10: Deployment, Optimization, Polish (0%)
- [ ] AWS deployment (ECS, RDS, CloudFront)
- [ ] Alembic database migrations for production
- [ ] Performance optimization (caching, CDN)
- [ ] Rate limiting
- [ ] Context window management for long conversations

---

## 🏗️ Architecture Highlights

### OCEAN (Big Five) Foundation

The system uses the **OCEAN personality model**, the most validated framework in psychology:

| Trait | Description | Low End | High End |
|-------|-------------|---------|----------|
| **O**penness | Curiosity, creativity | Conventional | Imaginative |
| **C**onscientiousness | Organization, discipline | Spontaneous | Organized |
| **E**xtraversion | Sociability, energy | Introverted | Outgoing |
| **A**greeableness | Compassion, cooperation | Skeptical | Trusting |
| **N**euroticism | Emotional stability | Calm | Anxious |

### 8 Archetypes

| Code | Name | Primary Traits |
|------|------|----------------|
| `ANALYST` | The Analyst | High C, Low E, Low A |
| `SOCIALITE` | The Socialite | High E, High A, Low C |
| `INNOVATOR` | The Innovator | High O, Moderate E |
| `ACTIVIST` | The Activist | High O, High A, High E |
| `PRAGMATIST` | The Pragmatist | Balanced, Low N |
| `TRADITIONALIST` | The Traditionalist | Low O, High C, High A |
| `SKEPTIC` | The Skeptic | High O, Low A, Low E |
| `OPTIMIST` | The Optimist | High E, High A, High O |

### Persona Creation Pipeline

```
POST /personas
    │
    ├─ 1. ContentModerationService.analyze_toxicity(description)
    │      → blocks with 400 + audit log if toxic; fail-open if service down
    │
    ├─ 2. OceanInferenceService.infer_ocean_traits(description)
    │      → Claude Haiku infers 5 OCEAN scores
    │
    ├─ 3. AffinityCalculator.calculate(ocean_vector)
    │      → cosine similarity → softmax → 8 archetype affinities
    │
    ├─ 4. LLMService.generate_motto(persona_details) [non-blocking]
    │      → Claude generates a personal motto
    │
    ├─ 5. ImageGenerationService.generate_avatar_for_persona() [non-blocking]
    │      → DALL-E generates avatar; fallback to DiceBear SVG
    │
    └─ 6. Persona saved to database → 201 Created
```

### Conversation Pipeline

```
POST /conversations/{id}/continue
    │
    ├─ Load participants + approved message history
    │
    └─ For each persona:
           │
           ├─ LLMService.generate_response(persona, history, topic)
           │
           ├─ ContentModerationService.analyze_toxicity(response)
           │
           ├─ If toxic: regenerate up to 2 times
           │
           └─ If still toxic: save as "flagged" + write ModerationAuditLog
```

---

## 🧪 Testing

### Test Coverage

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| `traits.py` | 19 | 95% | ✅ |
| `affinity.py` | 14 | 93% | ✅ |
| `archetypes.py` | 20 | 100% | ✅ |
| `ocean_inference.py` | ~20 | 85%+ | ✅ |
| `persona.py` (model) | ~15 | 85%+ | ✅ |
| `personas.py` (router) | ~30 | 85%+ | ✅ |
| `llm_service.py` | ~15 | 85%+ | ✅ |
| `image_generation_service.py` | ~15 | 85%+ | ✅ |
| `prompt_templates.py` | ~15 | 85%+ | ✅ |
| `content_moderation_service.py` | ~15 | 85%+ | ✅ |
| `moderation.py` (model) | ~10 | 94% | ✅ |
| `admin.py` (router) | ~10 | 100% | ✅ |
| `conversation.py` (model) | ~20 | 85%+ | ✅ |
| `conversation_orchestrator.py` | ~11 | 85%+ | ✅ |
| **Project Total** | **291** | **89%+** | ✅ |

### Running Tests

```bash
# Run all tests with coverage
cd backend && ./venv/bin/pytest tests/ -q

# Single file
./venv/bin/pytest tests/unit/test_conversation_orchestrator.py -v

# With coverage report
./venv/bin/pytest --cov=app --cov-report=html
```

---

## ⚠️ Known Gaps & Technical Debt

### Critical (needed for production)
- **No Alembic migrations** — `init_db()` uses `create_all()` which doesn't work for production schema changes. Alembic is installed but migrations haven't been generated.
- **OAuth callback returns JSON** — should redirect to frontend after login

### High Priority
- **All AI calls are synchronous** — OCEAN inference, motto, and avatar generation block the request thread. Should use async/background tasks.
- **No rate limiting** — endpoints have no request rate limits
- **No context window management** — long conversations could exceed Claude's token limit

### Medium Priority
- **No `PATCH /users/me`** — users cannot update their profile
- **No `/personas/preview`** — no way to preview OCEAN scores before saving
- **ModerationAuditLog `source_id`** — uses `"blocked_before_save"` for persona blocking since persona doesn't exist yet; could be improved by saving persona first and deleting on moderation failure

### Low Priority
- **OAuth CSRF state** stored in-memory dict (not Redis) — loses state on server restart
- **No `unique_id` collision retry** — 6-char alphanumeric has low but non-zero collision probability

---

## 📚 Documentation

### Core Documents
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Full 10-phase roadmap with TDD approach
- **[SCIENTIFIC_APPROACH.md](SCIENTIFIC_APPROACH.md)** - White paper on OCEAN methodology

### Technical Guides
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
- **[backend/OAUTH_SETUP_GUIDE.md](backend/OAUTH_SETUP_GUIDE.md)** - Google OAuth configuration

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Google OAuth credentials
- Anthropic API key (for OCEAN inference + motto generation)
- OpenAI API key (for avatar generation + content moderation)

### Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd ai-persona-app

# 2. Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys and OAuth credentials

# 3. Start services
docker-compose up backend

# 4. Access API
open http://localhost:8000/docs  # Swagger UI
```

### Environment Variables Required

```
DATABASE_URL=postgresql://...
JWT_SECRET=<random secret>
GOOGLE_CLIENT_ID=<from Google Console>
GOOGLE_CLIENT_SECRET=<from Google Console>
ANTHROPIC_API_KEY=<from Anthropic>
OPENAI_API_KEY=<from OpenAI>
```

---

## 📈 Roadmap

### Next Up (Phase 6) — Frontend
- [ ] Next.js frontend setup
- [ ] Persona management UI
- [ ] Conversation viewer

### Following (Phase 8-10) — Production
- [ ] Alembic migrations
- [ ] AWS deployment
- [ ] Rate limiting + async AI calls
- [ ] Performance optimization

---

## 🎯 Key Metrics

### Technical
- **Test Count:** 291 passing tests
- **Test Coverage:** 89%+ (target: 90%+)
- **Coverage Threshold:** 85% (enforced by CI)

### OCEAN System
- **Archetype Diversity:** 0.59 mean pairwise distance (good ✅)
- **Inference:** Claude Haiku (claude-haiku-4-5-20251001)
- **Affinity Consistency:** Deterministic (✅ validated in tests)

---

**Built with:**
- FastAPI (Python 3.11)
- PostgreSQL (database)
- NumPy (vector mathematics)
- Claude API / Anthropic SDK (OCEAN inference, conversation)
- OpenAI API (avatar generation, content moderation)
- Docker (containerization)
- pytest (testing)

**Designed for:**
- Researchers studying group dynamics
- Product teams testing ideas
- Educators teaching debate/discussion
- Anyone curious about AI conversations
