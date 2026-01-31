# AI Focus Groups

> **An AI-powered focus group application** where users create synthetic personas with distinct personalities and engage them in meaningful conversations about any topic.

[![Built with FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Frontend Next.js](https://img.shields.io/badge/Frontend-Next.js-000000.svg)](https://nextjs.org/)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://github.com/anthropics/claude-code)
[![TDD](https://img.shields.io/badge/methodology-TDD-blue.svg)](#test-driven-development)

## 🎯 Project Overview

**AI Focus Groups** allows users to:
- **Generate AI Personas** with unique personalities, backgrounds, and visual avatars
- **Create Focus Groups** by assembling multiple personas
- **Facilitate Discussions** on any topic, watching personas debate and interact
- **Share Results** via public links to personas and conversation logs

### Core Innovation: Personality Vector Space

Personas are not random - they're mathematically positioned in a 2D personality space using Euclidean distance weighting across multiple archetypal dimensions. This ensures consistent, representative, and diverse persona behaviors.

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Test-Driven Development](#-test-driven-development)
- [Development Workflow](#-development-workflow)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Phase Implementation](#-phase-implementation)

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [Python 3.11+](https://www.python.org/) (for local backend development)
- [Node.js 18+](https://nodejs.org/) (for frontend development)
- [Git](https://git-scm.com/)

### Local Development Setup

#### Option 1: Full Docker Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ai-persona-app

# Start backend + database
docker-compose up backend

# The API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### Option 2: Local Python Development

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Run tests (TDD!)
pytest -v

# Start development server
uvicorn app.main:app --reload

# API available at http://localhost:8000
```

---

## 🏗️ Architecture

### Modern 2026 Stack

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│  Next.js 14+ (React, TypeScript, Tailwind CSS)            │
│  SEO-optimized, shareable links (/p/xxx, /c/xxx)          │
└─────────────────────────────────────────────────────────────┘
                             ↓ REST API
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  • Authentication (JWT)                                     │
│  • Persona Generation (Vector Math + LLM)                  │
│  • Conversation Orchestration                               │
│  • Content Moderation                                       │
└─────────────────────────────────────────────────────────────┘
        ↓                    ↓                    ↓
  ┌──────────┐      ┌──────────────┐      ┌──────────────┐
  │   RDS    │      │  LLM APIs    │      │  Image Gen   │
  │PostgreSQL│      │(OpenAI/      │      │  (DALL-E/    │
  │          │      │ Anthropic)   │      │OpenJourney)  │
  └──────────┘      └──────────────┘      └──────────────┘
                             ↓
                    ┌──────────────────┐
                    │  AWS ECS/Fargate │
                    │   (Production)   │
                    └──────────────────┘
```

### Key Technologies

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **Frontend**: Next.js 14+, React, TypeScript, Tailwind CSS
- **Database**: PostgreSQL (AWS RDS in production)
- **AI**: OpenAI GPT-4 / Anthropic Claude, DALL-E / OpenJourney
- **Infrastructure**: Docker, AWS ECS/Fargate, Terraform
- **CI/CD**: GitHub Actions
- **Testing**: pytest, Jest, React Testing Library, Playwright

---

## 🧪 Test-Driven Development

**This project strictly follows TDD methodology.** All code is written using the Red-Green-Refactor cycle.

### Why TDD?

1. **Mathematical Correctness**: Personality vector calculations must be precise
2. **AI Consistency**: LLM behavior needs predictable validation
3. **Content Safety**: Moderation is critical and must be thoroughly tested
4. **Public Shareability**: Bugs are visible to the world - tests prevent embarrassment
5. **Cost Control**: LLM API costs are optimized through testing
6. **Team Onboarding**: Tests serve as executable documentation

### The TDD Cycle

```
┌──────────────────────────────────────────────────────┐
│  1. RED: Write a failing test                        │
│     • Define desired behavior                        │
│     • Test MUST fail initially                       │
└──────────────────┬───────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────┐
│  2. GREEN: Write minimal code to pass                │
│     • Just enough to make test pass                  │
│     • Don't over-engineer                            │
└──────────────────┬───────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────┐
│  3. REFACTOR: Improve code while keeping tests green │
│     • Remove duplication                             │
│     • Improve structure                              │
│     • Tests must still pass!                         │
└──────────────────────────────────────────────────────┘
```

### Running Tests

```bash
# Backend tests
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_vector_engine.py -v

# Run tests in watch mode (auto-run on file change)
ptw

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Coverage Requirements

| Code Type | Coverage Target |
|-----------|----------------|
| Business Logic (vector math, orchestration) | 95%+ |
| API Endpoints | 90%+ |
| Database Models | 85%+ |
| Frontend Components | 80%+ |
| **Overall** | **90%+** |

---

## 💻 Development Workflow

### Daily TDD Workflow

#### Morning Routine

```bash
# 1. Pull latest code
git pull origin main

# 2. Run tests (must pass before starting work)
cd backend && pytest
cd frontend && npm test

# 3. Identify feature to implement
# 4. Write test FIRST
```

#### Development Cycle

```bash
# 1. Create feature branch
git checkout -b feature/persona-vector-engine

# 2. Write failing test
# tests/unit/test_personality_calculator.py

# 3. Run test - confirm it FAILS
pytest tests/unit/test_personality_calculator.py

# 4. Write minimal implementation
# app/services/personality_calculator.py

# 5. Run test - confirm it PASSES
pytest tests/unit/test_personality_calculator.py

# 6. Refactor (keeping tests green)

# 7. Commit
git add .
git commit -m "feat: add personality weight calculation with tests"

# 8. Push
git push origin feature/persona-vector-engine
```

#### End of Day

```bash
# 1. Run full test suite
pytest --cov=app --cov-report=html

# 2. Check coverage report
open htmlcov/index.html

# 3. Ensure all tests pass
# 4. Push work
git push origin feature/persona-vector-engine
```

### Code Review Checklist

- [ ] Does PR include tests for all new code?
- [ ] Were tests written BEFORE implementation?
- [ ] Do all tests pass in CI?
- [ ] Is coverage maintained or improved?
- [ ] Are tests clear and well-named?
- [ ] Are edge cases covered?

---

## 📁 Project Structure

```
ai-persona-app/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── models/            # Database models (SQLAlchemy)
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── utils/             # Helper functions
│   ├── tests/
│   │   ├── conftest.py        # Shared pytest fixtures
│   │   ├── unit/              # Fast, isolated unit tests
│   │   └── integration/       # API and database tests
│   ├── alembic/               # Database migrations
│   ├── pytest.ini             # Pytest configuration
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development/test dependencies
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                   # Next.js frontend (Phase 6+)
│   ├── app/                   # App Router pages
│   ├── components/            # React components
│   ├── lib/                   # Utilities
│   ├── __tests__/             # Jest tests
│   ├── e2e/                   # Playwright E2E tests
│   └── package.json
│
├── infrastructure/             # Terraform IaC (Phase 8+)
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── modules/
│
├── legacy/                     # Old implementation (archived)
│   └── code/                  # Original Flask/Dash app
│
├── docker-compose.yml         # Local development orchestration
├── IMPLEMENTATION_PLAN.md     # Detailed phase-by-phase plan
├── README.md                  # This file
└── .github/
    └── workflows/             # CI/CD pipelines
        ├── backend-ci.yml
        ├── frontend-ci.yml
        └── deploy.yml
```

---

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test types
pytest -m unit           # Only unit tests (fast)
pytest -m integration    # Only integration tests
pytest -m slow           # Only slow tests

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_vector_engine.py

# Run tests matching pattern
pytest -k "test_personality"

# Run with print statements visible
pytest -s

# Run until first failure
pytest -x

# Run last failed tests
pytest --lf
```

### Continuous Testing

```bash
# Auto-run tests on file changes (recommended during development)
ptw  # pytest-watch

# In a separate terminal, watch code and tests simultaneously
```

---

## 🚀 Deployment

### Production Deployment (AWS ECS)

Deployment is automated via GitHub Actions. Pushing to `main` triggers:

1. **CI Pipeline**:
   - Lint checks (flake8, eslint)
   - Type checking (mypy, tsc)
   - **Tests must pass** (blocking)
   - Coverage requirements enforced
   - Docker images built

2. **CD Pipeline** (only if CI passes):
   - Terraform apply
   - Docker images pushed to ECR
   - ECS services updated
   - Smoke tests run

### Manual Deployment

```bash
# Deploy infrastructure
cd infrastructure/environments/prod
terraform init
terraform plan
terraform apply

# Build and push Docker images
docker build -t backend:latest backend/
docker tag backend:latest <ecr-url>/backend:latest
docker push <ecr-url>/backend:latest

# Update ECS service
aws ecs update-service --cluster ai-focus-groups --service backend --force-new-deployment
```

---

## 📈 Phase Implementation

This project is being built in phases following the [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md):

### ✅ Phase 1: Infrastructure & Scaffolding (CURRENT)
- ✅ Repository structure
- ✅ Testing infrastructure (pytest, Jest)
- ✅ Docker configuration
- ✅ FastAPI app initialization
- ✅ First TDD cycle (health endpoint)

### 🔄 Phase 2: Core Backend Services (NEXT)
- [ ] Database models (SQLAlchemy)
- [ ] Authentication system (JWT)
- [ ] Basic CRUD endpoints

### 📅 Future Phases
- **Phase 3**: Persona Vector Space Engine
- **Phase 4**: AI Integration (LLM & Image Generation)
- **Phase 5**: Content Moderation System
- **Phase 6**: Frontend Development (Next.js)
- **Phase 7**: Focus Group / Conversation System
- **Phase 8**: Deployment & CI/CD
- **Phase 9**: Testing & Optimization
- **Phase 10**: Polish & Launch Preparation

---

## 🤝 Contributing

1. **Follow TDD**: Write tests before code
2. **Maintain Coverage**: Don't decrease test coverage
3. **Write Clear Tests**: Test names should explain what they test
4. **Check Phase Plan**: Refer to [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

---

## 📖 Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed phase-by-phase plan
- [Project Specification](legacy/code/CLAUDE.md) - Original requirements
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)
- [Legacy Code](legacy/README.md) - Original Flask/Dash implementation

---

## 📝 License

[Your License Here]

---

## 🔗 Links

- **Production**: [personacomposer.app](https://personacomposer.app) *(coming soon)*
- **API Docs**: http://localhost:8000/docs (local)
- **Issues**: GitHub Issues
- **Design**: [Miro Board](https://miro.com/app/board/o9J_l3Gv7S0=/)

---

**Built with ❤️ using Test-Driven Development**

> "Legacy code is code without tests." - Michael Feathers

Don't create legacy code from day one. Start with tests. ✅
