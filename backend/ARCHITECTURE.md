# AI Focus Groups - Architecture Documentation

## System Architecture Diagrams

### 1. Class Diagram - Database Models & Core Components

```mermaid
classDiagram
    class User {
        +int id
        +string email
        +string google_id
        +string name
        +string picture_url
        +datetime created_at
        +datetime updated_at
        +to_dict() dict
        +normalize_email(email) string
    }

    class Settings {
        +string ENV
        +bool DEBUG
        +bool TESTING
        +string DATABASE_URL
        +string JWT_SECRET
        +string JWT_ALGORITHM
        +int JWT_EXPIRATION_MINUTES
        +string GOOGLE_CLIENT_ID
        +string GOOGLE_CLIENT_SECRET
        +string GOOGLE_REDIRECT_URI
        +string GOOGLE_SCOPES
        +google_scopes_list() List~string~
        +is_testing() bool
        +is_production() bool
    }

    class AuthModule {
        +create_access_token(user_id, expires_delta) string
        +decode_access_token(token) dict
        +verify_token(token) int
        +generate_oauth_state() string
        +verify_oauth_state(state) bool
        +cleanup_expired_states() void
    }

    class OAuth {
        +google: OAuthProvider
        +authorize_redirect(request, redirect_uri, state) Response
        +authorize_access_token(request) dict
    }

    class AuthRouter {
        +GET /auth/login/google
        +GET /auth/callback/google
    }

    class Database {
        +engine: Engine
        +SessionLocal: sessionmaker
        +Base: DeclarativeBase
        +get_db() Generator
        +init_db() void
        +drop_db() void
    }

    %% Relationships
    User --> Database : stored in
    AuthModule --> Settings : uses
    AuthRouter --> AuthModule : depends on
    AuthRouter --> OAuth : uses
    AuthRouter --> User : creates/updates
    AuthRouter --> Database : accesses

    note for User "OAuth-based authentication\nNo password storage\ngoogle_id is unique identifier"
    note for AuthModule "JWT token management\nOAuth state handling\nCSRF protection"
```

### 2. OAuth Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Google
    participant Database

    User->>Frontend: Click "Login with Google"
    Frontend->>Backend: GET /auth/login/google
    Backend->>Backend: generate_oauth_state()
    Backend->>Backend: Store state (CSRF protection)
    Backend-->>Frontend: 302 Redirect to Google OAuth
    Frontend->>Google: Redirect user to authorization page

    User->>Google: Sign in & authorize app
    Google-->>Frontend: 302 Redirect to callback URL
    Frontend->>Backend: GET /auth/callback/google?code=xxx&state=yyy

    Backend->>Backend: verify_oauth_state(state)
    alt State invalid or expired
        Backend-->>Frontend: 400 Bad Request
    end

    Backend->>Google: Exchange code for access token
    Google-->>Backend: Access token + user info

    Backend->>Database: Query user by google_id
    alt User exists
        Database-->>Backend: Return existing user
        Backend->>Database: Update user info (name, picture)
    else User doesn't exist
        Backend->>Database: Create new user
        Database-->>Backend: Return new user
    end

    Backend->>Backend: create_access_token(user.id)
    Backend-->>Frontend: 200 OK {access_token, user}
    Frontend->>Frontend: Store JWT token

    Note over User,Database: User is now authenticated!

    User->>Frontend: Access protected resource
    Frontend->>Backend: GET /api/resource<br/>Authorization: Bearer <token>
    Backend->>Backend: verify_token(token)
    Backend->>Database: Get user by ID from token
    Database-->>Backend: Return user
    Backend-->>Frontend: 200 OK {resource data}
```

### 3. Component Architecture

```mermaid
graph TB
    subgraph "Frontend Layer (Next.js)"
        FE[Next.js App]
        AUTH[Auth Components]
        UI[UI Components]
    end

    subgraph "API Layer (FastAPI)"
        MAIN[main.py<br/>FastAPI App]
        MIDDLEWARE[Middleware<br/>CORS, Sessions]
        ROUTES[Routers]

        subgraph "Routers"
            AUTH_ROUTER[auth.py<br/>OAuth Endpoints]
            FUTURE[personas.py<br/>conversations.py<br/><i>Phase 3+</i>]
        end
    end

    subgraph "Business Logic Layer"
        AUTH_MOD[auth.py<br/>JWT & OAuth Utils]
        CONFIG[config.py<br/>Settings]
        MODELS[Models]

        subgraph "Models"
            USER_MODEL[user.py<br/>User Model]
            PERSONA_MODEL[persona.py<br/><i>Phase 3</i>]
        end
    end

    subgraph "Data Layer"
        DB[database.py<br/>SQLAlchemy Engine]
        POSTGRES[(PostgreSQL<br/>AWS RDS)]
        SQLITE[(SQLite<br/>In-Memory Tests)]
    end

    subgraph "External Services"
        GOOGLE[Google OAuth 2.0]
        CLAUDE[Claude API<br/><i>Phase 4</i>]
        DALLE[DALL-E API<br/><i>Phase 4</i>]
    end

    %% Connections
    FE --> AUTH
    FE --> UI
    AUTH --> MAIN
    UI --> MAIN

    MAIN --> MIDDLEWARE
    MIDDLEWARE --> ROUTES
    ROUTES --> AUTH_ROUTER
    ROUTES -.-> FUTURE

    AUTH_ROUTER --> AUTH_MOD
    AUTH_ROUTER --> USER_MODEL
    AUTH_MOD --> CONFIG

    USER_MODEL --> DB
    PERSONA_MODEL -.-> DB

    DB --> POSTGRES
    DB -.-> SQLITE

    AUTH_ROUTER --> GOOGLE
    FUTURE -.-> CLAUDE
    FUTURE -.-> DALLE

    classDef implemented fill:#90EE90
    classDef planned fill:#FFE4B5
    classDef external fill:#87CEEB

    class FE,MAIN,MIDDLEWARE,AUTH_ROUTER,AUTH_MOD,CONFIG,USER_MODEL,DB,GOOGLE implemented
    class FUTURE,PERSONA_MODEL,CLAUDE,DALLE planned
    class POSTGRES,SQLITE,GOOGLE,CLAUDE,DALLE external
```

### 4. Database Schema (Current)

```mermaid
erDiagram
    USERS {
        int id PK "Auto-increment primary key"
        string email UK "Unique, lowercase, indexed"
        string google_id UK "Unique Google OAuth ID, indexed"
        string name "Optional display name"
        string picture_url "Optional profile picture"
        timestamp created_at "Creation timestamp"
        timestamp updated_at "Last update timestamp"
    }

    %% Future Phase 3+ relationships
    USERS ||--o{ PERSONAS : creates
    USERS ||--o{ CONVERSATIONS : initiates
    PERSONAS }o--|| USERS : belongs_to
    PERSONAS ||--o{ CONVERSATION_MESSAGES : participates_in
    CONVERSATIONS ||--o{ CONVERSATION_MESSAGES : contains
    CONVERSATIONS }o--|| USERS : belongs_to

    PERSONAS {
        int id PK
        int user_id FK
        string name
        text system_prompt
        float openness "0.0-1.0"
        float conscientiousness "0.0-1.0"
        float extraversion "0.0-1.0"
        float agreeableness "0.0-1.0"
        float neuroticism "0.0-1.0"
        string avatar_url
        timestamp created_at
    }

    CONVERSATIONS {
        int id PK
        int user_id FK
        string title
        string status
        timestamp created_at
        timestamp completed_at
    }

    CONVERSATION_MESSAGES {
        int id PK
        int conversation_id FK
        int persona_id FK
        text content
        timestamp created_at
    }

    note for PERSONAS "Phase 3: Personality vectors\nEuclidean distance for diversity"
    note for CONVERSATIONS "Phase 7: Focus group sessions"
```

### 5. API Endpoints (Current & Planned)

```mermaid
graph LR
    subgraph "Health & Info"
        HEALTH[GET /health]
        ROOT[GET /]
    end

    subgraph "Authentication (Phase 2 ✅)"
        LOGIN[GET /auth/login/google]
        CALLBACK[GET /auth/callback/google]
        ME[GET /users/me<br/><i>planned</i>]
    end

    subgraph "Personas (Phase 3)"
        CREATE_PERSONA[POST /personas]
        LIST_PERSONAS[GET /personas]
        GET_PERSONA[GET /personas/:id]
        UPDATE_PERSONA[PUT /personas/:id]
        DELETE_PERSONA[DELETE /personas/:id]
        PERSONA_DIVERSITY[GET /personas/diversity-check]
    end

    subgraph "Conversations (Phase 7)"
        CREATE_CONV[POST /conversations]
        LIST_CONV[GET /conversations]
        GET_CONV[GET /conversations/:id]
        CONV_MESSAGES[GET /conversations/:id/messages]
    end

    subgraph "Admin (Phase 8)"
        ADMIN_USERS[GET /admin/users]
        ADMIN_STATS[GET /admin/stats]
    end

    classDef implemented fill:#90EE90
    classDef planned fill:#FFE4B5

    class HEALTH,ROOT,LOGIN,CALLBACK implemented
    class ME,CREATE_PERSONA,LIST_PERSONAS,GET_PERSONA,UPDATE_PERSONA,DELETE_PERSONA,PERSONA_DIVERSITY,CREATE_CONV,LIST_CONV,GET_CONV,CONV_MESSAGES,ADMIN_USERS,ADMIN_STATS planned
```

### 6. Testing Architecture

```mermaid
graph TB
    subgraph "Test Infrastructure"
        PYTEST[pytest]
        FIXTURES[conftest.py<br/>Test Fixtures]
        COVERAGE[pytest-cov<br/>Coverage Reports]
    end

    subgraph "Unit Tests (39 passing)"
        TEST_SETUP[test_setup.py<br/>12 tests]
        TEST_HEALTH[test_health_endpoint.py<br/>3 tests]
        TEST_USER_OAUTH[test_user_model_oauth.py<br/>8 tests]
        TEST_OAUTH_HANDLER[test_oauth_handler.py<br/>11 tests]
        TEST_PHASE1[test_phase_1_complete.py<br/>5 tests]
    end

    subgraph "Integration Tests"
        INT_OAUTH[OAuth Flow Integration<br/><i>covered in unit tests</i>]
        INT_API[API Endpoint Integration<br/><i>planned</i>]
    end

    subgraph "Test Database"
        SQLITE_MEM[(SQLite In-Memory<br/>Fast & Isolated)]
    end

    PYTEST --> FIXTURES
    PYTEST --> COVERAGE
    FIXTURES --> TEST_SETUP
    FIXTURES --> TEST_HEALTH
    FIXTURES --> TEST_USER_OAUTH
    FIXTURES --> TEST_OAUTH_HANDLER
    FIXTURES --> TEST_PHASE1

    TEST_USER_OAUTH --> SQLITE_MEM
    TEST_OAUTH_HANDLER --> SQLITE_MEM

    INT_OAUTH --> SQLITE_MEM
    INT_API -.-> SQLITE_MEM

    classDef implemented fill:#90EE90
    classDef planned fill:#FFE4B5

    class PYTEST,FIXTURES,COVERAGE,TEST_SETUP,TEST_HEALTH,TEST_USER_OAUTH,TEST_OAUTH_HANDLER,TEST_PHASE1,SQLITE_MEM,INT_OAUTH implemented
    class INT_API planned
```

### 7. Deployment Architecture (Planned - Phase 8)

```mermaid
graph TB
    subgraph "Client"
        BROWSER[Web Browser]
    end

    subgraph "AWS Infrastructure"
        subgraph "Frontend"
            VERCEL[Vercel<br/>Next.js Hosting]
        end

        subgraph "Backend Services"
            ALB[Application Load Balancer]

            subgraph "ECS Fargate"
                TASK1[FastAPI Task 1]
                TASK2[FastAPI Task 2]
                TASKN[FastAPI Task N]
            end
        end

        subgraph "Data Storage"
            RDS[(RDS PostgreSQL<br/>Multi-AZ)]
            S3[(S3<br/>Avatars & Assets)]
            REDIS[(ElastiCache Redis<br/>Session Cache)]
        end

        subgraph "Monitoring"
            CW[CloudWatch Logs]
            SENTRY[Sentry<br/>Error Tracking]
        end
    end

    subgraph "External Services"
        GOOGLE_EXT[Google OAuth]
        CLAUDE_EXT[Claude API]
        DALLE_EXT[DALL-E API]
    end

    BROWSER --> VERCEL
    BROWSER --> ALB
    VERCEL --> ALB

    ALB --> TASK1
    ALB --> TASK2
    ALB --> TASKN

    TASK1 --> RDS
    TASK1 --> S3
    TASK1 --> REDIS
    TASK2 --> RDS
    TASK2 --> S3
    TASK2 --> REDIS
    TASKN --> RDS
    TASKN --> S3
    TASKN --> REDIS

    TASK1 --> CW
    TASK1 --> SENTRY
    TASK1 --> GOOGLE_EXT
    TASK1 --> CLAUDE_EXT
    TASK1 --> DALLE_EXT

    classDef aws fill:#FF9900
    classDef external fill:#87CEEB

    class ALB,RDS,S3,REDIS,CW aws
    class VERCEL,GOOGLE_EXT,CLAUDE_EXT,DALLE_EXT external
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0.25
- **Database**: PostgreSQL (prod) / SQLite (test)
- **Authentication**:
  - Google OAuth 2.0 (authlib 1.3.0)
  - JWT sessions (python-jose 3.3.0)
- **Testing**: pytest 7.4.4 + pytest-asyncio + pytest-cov
- **HTTP Client**: httpx 0.26.0
- **Validation**: Pydantic 2.5.3

### Frontend (Planned)
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context / Zustand

### Infrastructure (Phase 8)
- **Cloud**: AWS (ECS Fargate, RDS, S3, ElastiCache)
- **Container**: Docker
- **Orchestration**: docker-compose (dev) / ECS (prod)
- **CI/CD**: GitHub Actions

## Current Implementation Status

### ✅ Completed (Phase 1 & 2)
- FastAPI application setup
- Health check endpoint
- Docker configuration
- Test infrastructure (pytest)
- Database configuration (SQLAlchemy)
- User model (OAuth-based)
- Google OAuth 2.0 authentication
- JWT session tokens
- OAuth callback handling
- Comprehensive test suite (39 tests passing)

### 🔄 In Progress
- Auth middleware for protected endpoints
- User profile endpoint (GET /users/me)

### 📋 Planned
- **Phase 3**: Persona model with personality vectors
- **Phase 4**: AI integration (Claude API)
- **Phase 5**: Content moderation
- **Phase 6**: Avatar generation
- **Phase 7**: Conversation system
- **Phase 8**: AWS deployment
- **Phase 9**: Performance optimization
- **Phase 10**: Admin dashboard

## Key Design Decisions

1. **OAuth-only Authentication**: Simplified security by removing password management
2. **Test-Driven Development**: All features have tests written first
3. **SQLite for Tests**: Fast, isolated test database (in-memory)
4. **JWT for Sessions**: Stateless authentication after OAuth
5. **Personality Vectors**: 5-dimensional OCEAN model for AI personas
6. **Euclidean Distance**: Ensures diverse persona generation

---

**Last Updated**: 2026-01-31
**Phase**: 2 (OAuth Authentication) - Complete ✅
