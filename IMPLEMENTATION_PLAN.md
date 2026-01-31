# AI Focus Groups - Phased Implementation Plan

## Executive Summary
This document outlines a systematic, phase-by-phase approach to building the AI Focus Groups application. Each phase is designed to build upon the previous one, ensuring a stable foundation before adding complexity.

**Estimated Total Phases:** 10
**Architecture:** Modern 2026 stack with Next.js frontend, Python/FastAPI backend, AWS RDS database, fully Dockerized, deployed on AWS ECS/Fargate
**Development Methodology:** Test-Driven Development (TDD) - All tests must be written BEFORE implementation code

---

## Test-Driven Development (TDD) Approach

**CRITICAL REQUIREMENT:** This project follows strict TDD methodology. For every feature:

### The Red-Green-Refactor Cycle:
1. **RED**: Write a failing test that defines the desired behavior
2. **GREEN**: Write the minimal code to make the test pass
3. **REFACTOR**: Improve the code while keeping tests green

### TDD Guidelines:
- **Never write production code without a failing test first**
- Write tests at multiple levels:
  - **Unit Tests**: Individual functions, classes, and methods
  - **Integration Tests**: API endpoints, database interactions, service integrations
  - **E2E Tests**: Complete user flows (frontend)
- Use mocking/stubbing for external dependencies (LLM APIs, image generation)
- Aim for 90%+ test coverage
- Tests should be:
  - **Fast**: Run in milliseconds (use mocks for slow operations)
  - **Isolated**: No dependencies between tests
  - **Repeatable**: Same result every time
  - **Self-validating**: Clear pass/fail with descriptive messages
  - **Timely**: Written immediately before implementation

### Testing Stack:
- **Backend (Python)**: pytest, pytest-asyncio, pytest-cov, unittest.mock, faker
- **Frontend (Next.js)**: Jest, React Testing Library, Playwright/Cypress (E2E)
- **API Testing**: pytest with httpx, TestClient from FastAPI
- **Database**: Use test database or SQLite in-memory for speed

### TDD Workflow Example:
```python
# 1. Write the test FIRST (test_persona_service.py)
def test_calculate_personality_weights():
    calculator = PersonalityCalculator()
    weights = calculator.calculate_personality_weights(x=0.5, y=0.5)

    assert isinstance(weights, dict)
    assert sum(weights.values()) == pytest.approx(1.0)
    assert all(0 <= w <= 1 for w in weights.values())

# 2. Run test - it FAILS (no PersonalityCalculator exists yet)

# 3. Write minimal code to pass (persona_service.py)
class PersonalityCalculator:
    def calculate_personality_weights(self, x: float, y: float) -> Dict[str, float]:
        return {"The Skeptic": 1.0}  # Minimal implementation

# 4. Run test - it PASSES

# 5. Refactor and add more test cases
```

---

## Phase 1: Infrastructure & Scaffolding
**Goal:** Establish the foundational infrastructure and project structure with TDD setup.

### Deliverables:
- [ ] **Repository Structure**
  - Create monorepo structure with clear separation: `/frontend`, `/backend`, `/infrastructure`, `/shared`
  - Set up test directories: `/backend/tests`, `/frontend/__tests__`
  - Set up `.gitignore`, `.dockerignore`, and environment templates
  - Create `README.md` with setup instructions including TDD workflow

- [ ] **Testing Infrastructure Setup (DO THIS FIRST)**
  - **Backend Testing Setup:**
    - Install pytest, pytest-asyncio, pytest-cov, pytest-mock
    - Create `pytest.ini` with test configuration
    - Set up test fixtures directory
    - Create `conftest.py` with common fixtures (test database, test client)
    - Configure coverage reporting (target: 90%+)
  - **Frontend Testing Setup:**
    - Configure Jest with Next.js
    - Set up React Testing Library
    - Install Playwright or Cypress for E2E tests
    - Create test utilities and custom matchers
  - **CI Test Integration:**
    - Configure tests to run in Docker
    - Set up test database containers

- [ ] **Docker Configuration**
  - Create `Dockerfile` for Next.js frontend
  - Create `Dockerfile` for Python/FastAPI backend
  - Create `docker-compose.yml` for local development
  - Include PostgreSQL container for local dev
  - Include test database container
  - Configure hot-reload for both frontend and backend

- [ ] **Infrastructure as Code (Terraform)**
  - Initialize Terraform project in `/infrastructure`
  - Define VPC, subnets, and security groups
  - Define RDS PostgreSQL instance configuration
  - Define ECS cluster and task definitions
  - Define Application Load Balancer
  - Create separate environments: `dev`, `staging`, `prod`

- [ ] **AWS RDS Database**
  - Design initial schema (users, personas, conversations tables)
  - Create migration scripts using Alembic (Python)
  - Set up connection pooling and environment-based configs

- [ ] **Local Development Environment**
  - Verify `docker-compose up` works end-to-end
  - Test hot-reload for frontend and backend
  - Verify database connectivity

### Success Criteria:
- Developers can run `docker-compose up` and see "Hello World" from both frontend and backend
- Terraform can provision infrastructure in AWS (dry-run)
- Database migrations run successfully

---

## Phase 2: Core Backend Services (FastAPI Foundation)
**Goal:** Build the foundational backend API structure with authentication and basic CRUD operations using TDD.

### TDD Order of Implementation:
For each feature, follow this sequence: Write Tests → Run (Fail) → Implement → Run (Pass) → Refactor

### Deliverables:

#### 2.1 FastAPI Application Setup
- [ ] **WRITE TESTS FIRST:**
  - `test_app_initialization.py`: Test app starts, CORS configured
  - `test_health_endpoint.py`: Test `/health` returns 200
- [ ] **IMPLEMENT:**
  - Initialize FastAPI project structure (`/app`, `/models`, `/routes`, `/services`, `/utils`)
  - Set up CORS middleware for Next.js integration
  - Configure logging and error handling
  - Add health check endpoint (`/health`)

#### 2.2 Database Models (SQLAlchemy ORM)
- [ ] **WRITE TESTS FIRST:**
  - `test_user_model.py`: Test user creation, validation, unique email constraint
  - `test_persona_model.py`: Test persona creation, relationships, unique_id generation
  - `test_conversation_model.py`: Test conversation creation, participant relationships
  - `test_message_model.py`: Test message creation, timestamp ordering
- [ ] **IMPLEMENT:**
  - `User` model (id, email, password_hash, created_at, updated_at)
  - `Persona` model (id, user_id, unique_id, name, age, gender, description, attitude, model_used, personality_vector, motto, avatar_url, created_at)
  - `Conversation` model (id, unique_id, topic, created_by, created_at)
  - `ConversationMessage` model (id, conversation_id, persona_id, message_text, timestamp, toxicity_score)

#### 2.3 Authentication System
- [ ] **WRITE TESTS FIRST:**
  - `test_auth_registration.py`: Test user registration success, duplicate email rejection, password validation
  - `test_auth_login.py`: Test successful login, wrong password, nonexistent user
  - `test_jwt_tokens.py`: Test token generation, validation, expiration, refresh
  - `test_password_hashing.py`: Test bcrypt hashing and verification
  - `test_auth_middleware.py`: Test protected endpoints require valid token
- [ ] **IMPLEMENT:**
  - JWT token generation and validation functions
  - Password hashing utilities (bcrypt)
  - `POST /auth/register` endpoint
  - `POST /auth/login` endpoint
  - `POST /auth/refresh` endpoint
  - Authentication middleware/dependencies

#### 2.4 Basic CRUD Endpoints
- [ ] **WRITE TESTS FIRST:**
  - `test_user_endpoints.py`: Test `GET /users/me`, `PATCH /users/me` with auth
  - `test_persona_crud.py`: Test create, read, list, delete personas
  - `test_persona_authorization.py`: Test users can only access their own personas
  - `test_unique_id_generation.py`: Test 6-char unique IDs are collision-free
- [ ] **IMPLEMENT:**
  - User profile endpoints (`GET /users/me`, `PATCH /users/me`)
  - Persona endpoints (without AI generation):
    - `POST /personas` (create placeholder)
    - `GET /personas/{unique_id}` (retrieve)
    - `GET /personas` (list user's personas)
    - `DELETE /personas/{unique_id}`

#### 2.5 API Documentation
- [ ] Ensure FastAPI auto-generated docs are complete
- [ ] Add request/response examples
- [ ] Document authentication flow

### Success Criteria:
- **All tests pass** (100% for implemented features)
- Test coverage > 90% for this phase
- Users can register and login via API
- JWT tokens are issued and validated correctly
- Basic persona CRUD works (without AI features)
- API documentation is accessible at `/docs`
- CI pipeline runs all tests automatically

---

## Phase 3: Persona Vector Space Engine
**Goal:** Implement the mathematical personality engine using vector space and archetypes with TDD.

### TDD Order: This is a math-heavy feature - perfect for test-first development!

### Deliverables:

#### 3.1 Archetypes Configuration
- [ ] **WRITE TESTS FIRST:**
  - `test_archetypes_config.py`: Test archetype JSON loads correctly, has required fields
  - `test_archetype_validation.py`: Test coordinates are within bounds, no duplicate names
- [ ] **IMPLEMENT:**
  - Create `personas.json` with archetype definitions
  - Define 8-12 archetypes with: name, description, coordinates (x, y), trait weights
  - Examples: "The Skeptic", "The Optimist", "The Traditionalist", "The Progressive", "The Pragmatist"

#### 3.2 Vector Math Module (TDD is ESSENTIAL here)
- [ ] **WRITE TESTS FIRST (`test_vector_engine.py`):**
  ```python
  # Test Euclidean distance calculation
  def test_euclidean_distance():
      assert euclidean_distance(0, 0, 3, 4) == 5.0
      assert euclidean_distance(0, 0, 0, 0) == 0.0

  # Test weighted blending
  def test_weighted_blending():
      distances = {"A": 1.0, "B": 2.0, "C": 3.0}
      weights = calculate_weights(distances)
      assert sum(weights.values()) == pytest.approx(1.0)
      assert weights["A"] > weights["B"] > weights["C"]  # Closer = higher weight

  # Test normalization
  def test_normalization():
      values = {"A": 2.0, "B": 3.0, "C": 5.0}
      normalized = normalize_weights(values)
      assert sum(normalized.values()) == pytest.approx(1.0)

  # Test edge cases
  def test_exact_archetype_match():
      # When pin is exactly on an archetype, that archetype should have weight ~1.0
      weights = calculate_personality_weights(x=0.5, y=0.5)  # Assuming archetype at (0.5, 0.5)
      # Implementation should handle divide-by-zero gracefully

  def test_equidistant_archetypes():
      # When pin is equidistant from multiple archetypes, they should have equal weights
      pass
  ```
- [ ] **IMPLEMENT (`/backend/app/services/vector_engine.py`):**
  - Implement `euclidean_distance(x1, y1, x2, y2) -> float`
  - Implement `calculate_weights(distances: Dict) -> Dict` (inverse distance weighting)
  - Implement `normalize_weights(values: Dict) -> Dict` (sum to 1.0)
  - Handle edge cases: exact matches, divide-by-zero

#### 3.3 Personality Calculator Service
- [ ] **WRITE TESTS FIRST (`test_personality_calculator.py`):**
  ```python
  def test_personality_calculator_initialization():
      calculator = PersonalityCalculator(archetypes_path="personas.json")
      assert len(calculator.archetypes) >= 8

  def test_calculate_personality_weights_returns_dict():
      calculator = PersonalityCalculator()
      weights = calculator.calculate_personality_weights(x=0.5, y=0.5)
      assert isinstance(weights, dict)
      assert all(isinstance(k, str) for k in weights.keys())
      assert all(isinstance(v, float) for v in weights.values())

  def test_weights_sum_to_one():
      calculator = PersonalityCalculator()
      weights = calculator.calculate_personality_weights(x=0.3, y=0.7)
      assert sum(weights.values()) == pytest.approx(1.0)

  def test_generate_personality_prompt():
      calculator = PersonalityCalculator()
      weights = {"The Skeptic": 0.6, "The Optimist": 0.4}
      prompt = calculator.generate_personality_prompt(weights)
      assert "Skeptic" in prompt
      assert "Optimist" in prompt
      assert isinstance(prompt, str)

  def test_coordinate_validation():
      calculator = PersonalityCalculator()
      with pytest.raises(ValueError):
          calculator.calculate_personality_weights(x=999, y=999)  # Out of bounds
  ```
- [ ] **IMPLEMENT:**
  - Create `PersonalityCalculator` class
  - Method: `calculate_personality_weights(x: float, y: float) -> Dict[str, float]`
  - Method: `generate_personality_prompt(weights: Dict) -> str` (for LLM context)
  - Add coordinate validation (bounds checking)

#### 3.4 Personality Grid API Endpoints
- [ ] **WRITE TESTS FIRST (`test_personality_api.py`):**
  ```python
  def test_get_archetypes_endpoint(client):
      response = client.get("/archetypes")
      assert response.status_code == 200
      data = response.json()
      assert isinstance(data, list)
      assert len(data) >= 8
      assert "name" in data[0]
      assert "coordinates" in data[0]

  def test_preview_personality_endpoint(client, auth_headers):
      response = client.post(
          "/personas/preview",
          json={"x": 0.5, "y": 0.5},
          headers=auth_headers
      )
      assert response.status_code == 200
      data = response.json()
      assert "weights" in data
      assert sum(data["weights"].values()) == pytest.approx(1.0)

  def test_preview_invalid_coordinates(client, auth_headers):
      response = client.post(
          "/personas/preview",
          json={"x": 999, "y": 999},
          headers=auth_headers
      )
      assert response.status_code == 422  # Validation error
  ```
- [ ] **IMPLEMENT:**
  - `GET /archetypes` - Return all archetype definitions
  - `POST /personas/preview` - Calculate personality weights without saving

#### 3.5 Database Integration
- [ ] **WRITE TESTS FIRST:**
  - `test_persona_with_vector.py`: Test storing and retrieving personality vector as JSON
- [ ] **IMPLEMENT:**
  - Store personality vector as JSONB column in `Persona` model
  - Add archetype weights to persona creation flow

#### 3.6 Documentation
- [ ] Add comprehensive docstrings explaining the math
- [ ] Create visual diagrams showing archetype placement
- [ ] Document how to add/modify archetypes

### Success Criteria:
- **All tests pass** (100%)
- Test coverage > 95% for vector math (this is pure logic, should be highly testable)
- Given coordinates (x, y), system correctly calculates weighted blend
- API returns consistent personality weights
- Edge cases handled: exact matches, out of bounds, equidistant points
- Frontend can fetch archetypes and preview personality calculations

---

## Phase 4: AI Integration (LLM & Image Generation)
**Goal:** Integrate external AI services using TDD with extensive mocking.

### TDD Strategy for External Services:
- Use mocks/stubs for all external API calls (LLM, image generation)
- Tests should run fast and not depend on external services
- Create separate integration tests (optional, run manually) that hit real APIs

### Deliverables:

#### 4.1 LLM Integration
- [ ] **WRITE TESTS FIRST (`test_llm_service.py`):**
  ```python
  @pytest.fixture
  def mock_openai_response():
      return {"choices": [{"message": {"content": "Live, Laugh, Love"}}]}

  def test_llm_service_initialization():
      llm_service = LLMService(provider="openai", api_key="test-key")
      assert llm_service.provider == "openai"

  @patch('openai.ChatCompletion.create')
  def test_generate_motto(mock_create, mock_openai_response):
      mock_create.return_value = mock_openai_response
      llm_service = LLMService(provider="openai")

      persona_details = {
          "name": "John",
          "personality_weights": {"The Optimist": 0.8, "The Pragmatist": 0.2}
      }
      motto = llm_service.generate_motto(persona_details)

      assert isinstance(motto, str)
      assert len(motto) > 0
      mock_create.assert_called_once()

  @patch('openai.ChatCompletion.create')
  def test_generate_response_includes_personality(mock_create):
      # Test that personality weights are included in the prompt
      llm_service = LLMService(provider="openai")
      persona_details = {"personality_weights": {"The Skeptic": 1.0}}

      llm_service.generate_response(persona_details, [], "Climate change")

      call_args = mock_create.call_args
      prompt = str(call_args)
      assert "Skeptic" in prompt

  def test_retry_logic_on_failure():
      # Test that LLM service retries on API failures
      llm_service = LLMService(provider="openai", max_retries=3)

      with patch('openai.ChatCompletion.create') as mock:
          mock.side_effect = [Exception("API Error"), Exception("API Error"), {"choices": [{"message": {"content": "Success"}}]}]
          result = llm_service.generate_motto({})
          assert result == "Success"
          assert mock.call_count == 3

  def test_token_counting():
      llm_service = LLMService(provider="openai")
      tokens = llm_service.count_tokens("Hello world")
      assert isinstance(tokens, int)
      assert tokens > 0
  ```

- [ ] **IMPLEMENT:**
  - Create `LLMService` class with provider abstraction
  - Implement methods:
    - `generate_motto(persona_details: dict) -> str`
    - `generate_response(persona_details: dict, conversation_history: list, topic: str) -> str`
    - `count_tokens(text: str) -> int`
  - Add retry logic (exponential backoff)
  - Add error handling and logging
  - Support multiple providers (OpenAI, Anthropic)

#### 4.2 Image Generation Integration
- [ ] **WRITE TESTS FIRST (`test_image_generation_service.py`):**
  ```python
  @patch('requests.post')
  def test_generate_avatar_dalle(mock_post):
      mock_post.return_value.json.return_value = {"data": [{"url": "https://example.com/image.png"}]}

      img_service = ImageGenerationService()
      url = img_service.generate_avatar(prompt="A friendly robot", model="dalle")

      assert url == "https://example.com/image.png"
      mock_post.assert_called_once()

  @patch('requests.post')
  def test_generate_avatar_openjourney(mock_post):
      mock_post.return_value.json.return_value = {"image_url": "https://example.com/image.png"}

      img_service = ImageGenerationService()
      url = img_service.generate_avatar(prompt="A wise sage", model="openjourney")

      assert url == "https://example.com/image.png"

  def test_fallback_on_generation_failure():
      img_service = ImageGenerationService()

      with patch('requests.post') as mock:
          mock.side_effect = Exception("API Error")
          url = img_service.generate_avatar(prompt="Test", model="dalle")

          # Should return fallback/default avatar
          assert "default-avatar" in url or "placeholder" in url

  def test_invalid_model_raises_error():
      img_service = ImageGenerationService()
      with pytest.raises(ValueError):
          img_service.generate_avatar(prompt="Test", model="invalid_model")
  ```

- [ ] **IMPLEMENT:**
  - Create `ImageGenerationService` class
  - Implement OpenJourney integration
  - Implement DALL-E integration
  - Method: `generate_avatar(prompt: str, model: str) -> str`
  - Handle image storage (S3 or direct URLs)
  - Add fallback/default avatars

#### 4.3 Prompt Engineering
- [ ] **WRITE TESTS FIRST (`test_prompt_templates.py`):**
  ```python
  def test_motto_prompt_includes_personality():
      template = MottoPromptTemplate()
      prompt = template.render(
          name="Alice",
          personality_weights={"The Optimist": 0.7, "The Idealist": 0.3},
          attitude="Comical"
      )

      assert "Alice" in prompt
      assert "Optimist" in prompt
      assert "Comical" in prompt

  def test_conversation_prompt_includes_history():
      template = ConversationPromptTemplate()
      history = [
          {"speaker": "Bob", "message": "I think taxes are too high"},
          {"speaker": "Carol", "message": "But we need public services"}
      ]

      prompt = template.render(
          persona_name="Alice",
          personality_weights={"The Pragmatist": 1.0},
          attitude="Neutral",
          topic="Tax policy",
          history=history
      )

      assert "Bob" in prompt
      assert "taxes are too high" in prompt
      assert "Tax policy" in prompt
  ```

- [ ] **IMPLEMENT:**
  - Create `PromptTemplate` base class
  - Create `MottoPromptTemplate` class
  - Create `ConversationPromptTemplate` class
  - Add context injection for attitude (Neutral, Sarcastic, Comical, Somber)

#### 4.4 API Configuration & Security
- [ ] **WRITE TESTS FIRST (`test_config.py`):**
  ```python
  def test_api_keys_loaded_from_env():
      with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
          config = AIConfig()
          assert config.openai_api_key == "test-key"

  def test_missing_api_key_raises_error():
      with patch.dict(os.environ, {}, clear=True):
          with pytest.raises(ValueError, match="OPENAI_API_KEY"):
              config = AIConfig()

  def test_rate_limiting():
      limiter = RateLimiter(max_requests=5, window_seconds=60)

      for i in range(5):
          assert limiter.allow_request() == True

      assert limiter.allow_request() == False  # 6th request should be blocked
  ```

- [ ] **IMPLEMENT:**
  - Set up environment variables for API keys
  - Create `AIConfig` class
  - Implement rate limiting (per-user, per-endpoint)
  - Add quota management

#### 4.5 Updated Persona Creation Flow
- [ ] **WRITE TESTS FIRST (`test_persona_creation_with_ai.py`):**
  ```python
  @patch('app.services.llm_service.LLMService.generate_motto')
  @patch('app.services.image_generation_service.ImageGenerationService.generate_avatar')
  def test_persona_creation_end_to_end(mock_generate_avatar, mock_generate_motto, client, auth_headers):
      mock_generate_motto.return_value = "Question everything"
      mock_generate_avatar.return_value = "https://example.com/avatar.png"

      response = client.post(
          "/personas",
          json={
              "name": "Alice",
              "age": 30,
              "gender": "Female",
              "description": "A thoughtful analyst",
              "attitude": "Neutral",
              "model": "dalle",
              "personality_coordinates": {"x": 0.5, "y": 0.5}
          },
          headers=auth_headers
      )

      assert response.status_code == 201
      data = response.json()
      assert data["motto"] == "Question everything"
      assert data["avatar_url"] == "https://example.com/avatar.png"

      mock_generate_motto.assert_called_once()
      mock_generate_avatar.assert_called_once()

  def test_persona_creation_handles_ai_failure_gracefully(client, auth_headers):
      # If AI services fail, persona should still be created with placeholders
      with patch('app.services.llm_service.LLMService.generate_motto') as mock:
          mock.side_effect = Exception("API Error")

          response = client.post("/personas", json={...}, headers=auth_headers)

          # Should return 201 with fallback motto
          assert response.status_code == 201
          assert "motto" in response.json()
  ```

- [ ] **IMPLEMENT:**
  - Update `POST /personas` to trigger:
    1. Vector calculation
    2. Motto generation (LLM)
    3. Avatar generation (Image AI)
    4. Database save
  - Add graceful fallbacks on AI failure
  - Optional: Add job queue (Celery/Redis) for async processing

### Success Criteria:
- **All tests pass** (100%)
- Tests run fast (< 5 seconds) using mocks
- Test coverage > 85% for AI integration code
- Persona creation works end-to-end with mocked AI services
- Optional integration tests can hit real APIs for validation
- API keys are securely managed (never committed to Git)
- Rate limiting prevents API abuse

---

## Phase 5: Content Moderation System
**Goal:** Implement safety layer to prevent toxic content using TDD.

### TDD Strategy:
- Use test fixtures with known toxic/safe examples
- Mock external moderation APIs
- Test threshold logic extensively

### Deliverables:

#### 5.1 Research & Decision
- [ ] **Research Existing Solutions:**
  - Evaluate OpenAI Moderation API
  - Evaluate Perspective API (Google Jigsaw)
  - Evaluate custom lightweight classifiers (DistilBERT-based)
  - **Recommendation:** Start with OpenAI Moderation API (fast, accurate, free)

#### 5.2 Moderation Service
- [ ] **WRITE TESTS FIRST (`test_content_moderation_service.py`):**
  ```python
  @pytest.fixture
  def safe_text():
      return "I think we should discuss this topic thoughtfully."

  @pytest.fixture
  def toxic_text():
      return "[Known toxic example for testing]"

  @patch('openai.Moderation.create')
  def test_analyze_toxicity_returns_score(mock_moderation):
      mock_moderation.return_value = {
          "results": [{"category_scores": {"hate": 0.001, "harassment": 0.002}}]
      }

      moderator = ContentModerationService()
      score = moderator.analyze_toxicity("Test text")

      assert isinstance(score, float)
      assert 0.0 <= score <= 1.0
      mock_moderation.assert_called_once()

  @patch('openai.Moderation.create')
  def test_safe_content_low_score(mock_moderation, safe_text):
      mock_moderation.return_value = {
          "results": [{"category_scores": {"hate": 0.001}}]
      }

      moderator = ContentModerationService()
      score = moderator.analyze_toxicity(safe_text)

      assert score < 0.1

  @patch('openai.Moderation.create')
  def test_toxic_content_high_score(mock_moderation, toxic_text):
      mock_moderation.return_value = {
          "results": [{"category_scores": {"hate": 0.95}}]
      }

      moderator = ContentModerationService()
      score = moderator.analyze_toxicity(toxic_text)

      assert score > 0.7

  def test_threshold_check():
      moderator = ContentModerationService(threshold=0.7)

      assert moderator.is_safe(toxicity_score=0.5) == True
      assert moderator.is_safe(toxicity_score=0.8) == False

  def test_fallback_on_api_failure():
      # If moderation API fails, should fail safely (block content)
      moderator = ContentModerationService()

      with patch('openai.Moderation.create') as mock:
          mock.side_effect = Exception("API Error")
          score = moderator.analyze_toxicity("Test")

          # Should return high score (fail safe)
          assert score >= 0.9
  ```

- [ ] **IMPLEMENT:**
  - Create `ContentModerationService` class
  - Method: `analyze_toxicity(text: str) -> float` (returns 0-1 score)
  - Method: `is_safe(toxicity_score: float) -> bool`
  - Implement chosen solution (OpenAI Moderation API)
  - Add thresholds configuration (environment-based)
  - Add fail-safe logic (block on API failure)

#### 5.3 Moderation Workflow
- [ ] **WRITE TESTS FIRST (`test_moderation_workflow.py`):**
  ```python
  @patch('app.services.content_moderation_service.ContentModerationService.analyze_toxicity')
  def test_persona_description_moderation(mock_analyze, client, auth_headers):
      mock_analyze.return_value = 0.95  # Toxic

      response = client.post(
          "/personas",
          json={
              "name": "Test",
              "description": "Toxic content here",
              ...
          },
          headers=auth_headers
      )

      assert response.status_code == 400
      assert "content moderation" in response.json()["detail"].lower()

  @patch('app.services.content_moderation_service.ContentModerationService.analyze_toxicity')
  def test_conversation_message_moderation(mock_analyze):
      mock_analyze.return_value = 0.85  # Toxic

      orchestrator = ConversationOrchestrator()
      result = orchestrator.generate_message(persona, topic, history)

      # Should either: regenerate, block, or flag
      assert result.moderation_status == "flagged" or result.regenerated == True

  def test_audit_log_on_flagged_content(db_session):
      # When content is flagged, it should be logged
      moderator = ContentModerationService()
      moderator.flag_content(
          content="Flagged message",
          toxicity_score=0.88,
          source="conversation_message",
          source_id=123
      )

      audit_log = db_session.query(ModerationAuditLog).first()
      assert audit_log.toxicity_score == 0.88
      assert audit_log.source_id == 123
  ```

- [ ] **IMPLEMENT:**
  - Check persona descriptions before save
  - Check conversation messages before display
  - If score > threshold:
    - Log incident to audit table
    - Option A: Regenerate with "make it safer" prompt
    - Option B: Block and return error to user
    - Option C: Soft flag for admin review (low priority)

#### 5.4 Database Schema Updates
- [ ] **WRITE TESTS FIRST (`test_moderation_models.py`):**
  ```python
  def test_conversation_message_with_toxicity_score(db_session):
      message = ConversationMessage(
          conversation_id=1,
          persona_id=1,
          message_text="Test message",
          toxicity_score=0.12,
          moderation_status="approved"
      )
      db_session.add(message)
      db_session.commit()

      retrieved = db_session.query(ConversationMessage).first()
      assert retrieved.toxicity_score == 0.12
      assert retrieved.moderation_status == "approved"

  def test_moderation_audit_log(db_session):
      log = ModerationAuditLog(
          content="Flagged content",
          toxicity_score=0.87,
          source="persona_description",
          source_id=42,
          action_taken="blocked"
      )
      db_session.add(log)
      db_session.commit()

      assert log.id is not None
      assert log.created_at is not None
  ```

- [ ] **IMPLEMENT:**
  - Add `toxicity_score` to `ConversationMessage` model
  - Add `moderation_status` field (approved, flagged, blocked)
  - Create `ModerationAuditLog` table

#### 5.5 Admin Dashboard (Basic)
- [ ] **WRITE TESTS FIRST (`test_admin_endpoints.py`):**
  ```python
  def test_get_flagged_content_requires_admin(client, user_headers):
      response = client.get("/admin/flagged-content", headers=user_headers)
      assert response.status_code == 403  # Forbidden

  def test_get_flagged_content_as_admin(client, admin_headers):
      response = client.get("/admin/flagged-content", headers=admin_headers)
      assert response.status_code == 200
      data = response.json()
      assert isinstance(data, list)

  def test_approve_flagged_content(client, admin_headers):
      response = client.post(
          "/admin/approve/123",
          headers=admin_headers
      )
      assert response.status_code == 200
  ```

- [ ] **IMPLEMENT:**
  - Add `is_admin` field to User model
  - Create admin authentication middleware
  - `GET /admin/flagged-content` - List flagged items
  - `POST /admin/approve/{message_id}` - Approve flagged content
  - `POST /admin/block/{message_id}` - Permanently block content

### Success Criteria:
- **All tests pass** (100%)
- Test coverage > 90% for moderation logic
- All generated content passes through moderation layer
- Toxic content is blocked or flagged correctly
- Moderation adds < 500ms latency (with mocking, tests should be instant)
- Admin can review flagged content
- Audit log records all moderation actions

---

## Phase 6: Frontend Development (Next.js)
**Goal:** Build user-facing web application with TDD approach for components and user flows.

### TDD Strategy for Frontend:
- **Component Testing**: Test component rendering, user interactions, state changes
- **Integration Testing**: Test API calls, form submissions, navigation
- **E2E Testing**: Test complete user journeys with Playwright/Cypress
- **Accessibility Testing**: Test with axe-core and keyboard navigation

### Deliverables:

#### 6.1 Next.js Application Setup
- [ ] **Set up testing infrastructure FIRST:**
  - Configure Jest with Next.js
  - Set up React Testing Library
  - Install and configure Playwright or Cypress
  - Create test utilities (`render`, `mockApiResponse`, etc.)
  - Set up MSW (Mock Service Worker) for API mocking
- [ ] **IMPLEMENT:**
  - Initialize Next.js 14+ with App Router
  - Set up TypeScript
  - Configure Tailwind CSS
  - Set up folder structure: `/app`, `/components`, `/lib`, `/types`, `/__tests__`

#### 6.2 Authentication UI
- [ ] **WRITE TESTS FIRST (`__tests__/auth/`):**
  ```typescript
  // test_login_page.test.tsx
  describe('Login Page', () => {
    test('renders login form', () => {
      render(<LoginPage />);
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });

    test('submits form with valid credentials', async () => {
      const mockLogin = jest.fn().mockResolvedValue({ token: 'abc123' });
      render(<LoginPage onLogin={mockLogin} />);

      await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
      await userEvent.type(screen.getByLabelText(/password/i), 'password123');
      await userEvent.click(screen.getByRole('button', { name: /login/i }));

      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });

    test('displays error on invalid credentials', async () => {
      // Mock API error response
      server.use(
        rest.post('/auth/login', (req, res, ctx) => {
          return res(ctx.status(401), ctx.json({ detail: 'Invalid credentials' }));
        })
      );

      render(<LoginPage />);
      // ... fill form ...
      await userEvent.click(screen.getByRole('button', { name: /login/i }));

      expect(await screen.findByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  // test_protected_routes.test.tsx
  test('redirects to login when accessing protected route without auth', () => {
    render(<ProtectedRoute><PersonaList /></ProtectedRoute>);
    expect(mockRouter.push).toHaveBeenCalledWith('/login');
  });
  ```

- [ ] **IMPLEMENT:**
  - Login page (`/login`)
  - Registration page (`/register`)
  - Auth context/state management (Context API or Zustand)
  - Protected route wrapper
  - JWT storage and refresh logic

#### 6.3 Persona Creation Page
- [ ] **WRITE TESTS FIRST (`__tests__/personas/creation.test.tsx`):**
  ```typescript
  describe('Persona Creation Form', () => {
    test('renders all form fields', () => {
      render(<PersonaCreationForm />);

      expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/age/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/gender/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/attitude/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/model/i)).toBeInTheDocument();
    });

    test('personality grid allows pin placement', async () => {
      render(<PersonalityGrid onCoordinatesChange={mockOnChange} />);

      const grid = screen.getByTestId('personality-grid');
      await userEvent.click(grid); // Click at specific coordinates

      expect(mockOnChange).toHaveBeenCalledWith({ x: expect.any(Number), y: expect.any(Number) });
    });

    test('shows real-time personality weight preview', async () => {
      server.use(
        rest.post('/personas/preview', (req, res, ctx) => {
          return res(ctx.json({ weights: { "The Skeptic": 0.7, "The Optimist": 0.3 } }));
        })
      );

      render(<PersonalityGrid />);
      await userEvent.click(screen.getByTestId('personality-grid'));

      expect(await screen.findByText(/The Skeptic: 70%/i)).toBeInTheDocument();
    });

    test('submits form and redirects on success', async () => {
      server.use(
        rest.post('/personas', (req, res, ctx) => {
          return res(ctx.status(201), ctx.json({ unique_id: 'abc123', ...req.body }));
        })
      );

      render(<PersonaCreationForm />);

      // Fill all fields...
      await userEvent.click(screen.getByRole('button', { name: /create/i }));

      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/p/abc123');
      });
    });

    test('shows loading state during creation', async () => {
      render(<PersonaCreationForm />);

      // Fill fields and submit...
      await userEvent.click(screen.getByRole('button', { name: /create/i }));

      expect(screen.getByRole('button', { name: /creating/i })).toBeDisabled();
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });
  ```

- [ ] **IMPLEMENT:**
  - Persona creation page (`/personas/new`)
  - Form fields: Name, Age, Gender, Description
  - Attitude selector dropdown
  - Model selector (OpenJourney, DALL-E)
  - **Personality Grid Component** (complex, needs thorough testing):
    - 2D Cartesian grid with archetypes
    - Drag/click to place pin
    - Real-time weight preview
  - Submit with loading states
  - Error handling
  - Redirect on success

#### 6.4 Persona Profile Page
- [ ] **WRITE TESTS FIRST (`__tests__/personas/profile.test.tsx`):**
  ```typescript
  describe('Persona Profile Page', () => {
    test('displays persona information', async () => {
      server.use(
        rest.get('/personas/:id', (req, res, ctx) => {
          return res(ctx.json({
            name: 'Alice',
            age: 30,
            motto: 'Question everything',
            avatar_url: 'https://example.com/avatar.png'
          }));
        })
      );

      render(<PersonaProfile id="abc123" />);

      expect(await screen.findByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('Question everything')).toBeInTheDocument();
      expect(screen.getByAltText('Alice avatar')).toHaveAttribute('src', 'https://example.com/avatar.png');
    });

    test('renders Open Graph meta tags', () => {
      render(<PersonaProfile id="abc123" />);

      const ogTitle = document.querySelector('meta[property="og:title"]');
      expect(ogTitle).toHaveAttribute('content', expect.stringContaining('Alice'));
    });

    test('shows CTA button', () => {
      render(<PersonaProfile id="abc123" />);

      const cta = screen.getByRole('button', { name: /start a conversation/i });
      expect(cta).toBeInTheDocument();
    });

    test('is publicly accessible (no auth required)', async () => {
      // Should render even without auth token
      render(<PersonaProfile id="abc123" />);

      expect(await screen.findByText('Alice')).toBeInTheDocument();
    });
  });
  ```

- [ ] **IMPLEMENT:**
  - Persona profile page (`/p/[id]`)
  - Display avatar, metadata, motto
  - Personality breakdown chart
  - CTA button
  - Open Graph tags

#### 6.5 Other Pages & Components
- [ ] **Write tests then implement:**
  - Persona library page (`/personas`) - test list rendering, search, delete
  - Layout/navigation - test responsive behavior, auth state display
  - SEO components - test metadata generation

#### 6.6 E2E Tests (Playwright/Cypress)
- [ ] **WRITE E2E TESTS:**
  ```typescript
  // e2e/persona-creation-flow.spec.ts
  test('complete persona creation flow', async ({ page }) => {
    await page.goto('/register');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await page.waitForURL('/personas');

    await page.click('text=Create New Persona');
    await page.fill('[name="name"]', 'Test Persona');
    await page.fill('[name="age"]', '25');
    await page.selectOption('[name="attitude"]', 'Neutral');
    await page.click('[data-testid="personality-grid"]', { position: { x: 100, y: 100 } });
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/p\/[a-z0-9]{6}/);
    await expect(page.locator('h1')).toContainText('Test Persona');
  });
  ```

### Success Criteria:
- **All tests pass** (100%)
- Test coverage > 80% for components
- All E2E user flows pass
- Accessibility score > 90 (axe-core)
- Users can register, login, and create personas
- Personality grid is interactive and intuitive
- Persona profile pages are shareable and SEO-friendly
- UI is responsive and passes mobile tests

---

## Phase 7: Focus Group / Conversation System
**Goal:** Build multi-persona conversation orchestration with TDD.

### TDD Strategy:
- Test orchestration logic extensively (core business logic)
- Mock LLM responses for predictable testing
- Test conversation flow state management
- Test moderation integration

### Deliverables:

#### 7.1 Conversation Backend
- [ ] **WRITE TESTS FIRST:**
  ```python
  # test_conversation_endpoints.py
  def test_create_conversation(client, auth_headers, test_personas):
      response = client.post(
          "/conversations",
          json={
              "topic": "Should we colonize Mars?",
              "persona_ids": [test_personas[0].id, test_personas[1].id]
          },
          headers=auth_headers
      )

      assert response.status_code == 201
      data = response.json()
      assert "unique_id" in data
      assert len(data["unique_id"]) == 6
      assert data["topic"] == "Should we colonize Mars?"

  def test_get_conversation_with_messages(client):
      response = client.get("/conversations/abc123")

      assert response.status_code == 200
      data = response.json()
      assert "messages" in data
      assert "participants" in data

  def test_continue_conversation(client, auth_headers, existing_conversation):
      response = client.post(
          f"/conversations/{existing_conversation.unique_id}/continue",
          headers=auth_headers
      )

      assert response.status_code == 200
      data = response.json()
      assert "new_messages" in data
      assert len(data["new_messages"]) > 0

  def test_conversation_length_limit(client, auth_headers, maxed_conversation):
      # Conversation already has 20 turns
      response = client.post(
          f"/conversations/{maxed_conversation.unique_id}/continue",
          headers=auth_headers
      )

      assert response.status_code == 400
      assert "maximum length" in response.json()["detail"].lower()
  ```

- [ ] **IMPLEMENT:**
  - `POST /conversations` - Create conversation
  - `GET /conversations/{id}` - Retrieve with messages
  - `POST /conversations/{id}/continue` - Generate next round
  - Add conversation length limits

#### 7.2 Conversation Orchestrator
- [ ] **WRITE TESTS FIRST (`test_conversation_orchestrator.py`):**
  ```python
  @patch('app.services.llm_service.LLMService.generate_response')
  @patch('app.services.content_moderation_service.ContentModerationService.analyze_toxicity')
  def test_orchestrator_generates_responses_for_all_personas(mock_moderation, mock_llm):
      mock_llm.return_value = "This is my opinion."
      mock_moderation.return_value = 0.1  # Safe

      orchestrator = ConversationOrchestrator()
      personas = [persona1, persona2, persona3]
      topic = "Climate change"

      messages = orchestrator.generate_turn(personas, topic, history=[])

      assert len(messages) == 3
      assert mock_llm.call_count == 3
      assert all(msg.moderation_status == "approved" for msg in messages)

  @patch('app.services.llm_service.LLMService.generate_response')
  @patch('app.services.content_moderation_service.ContentModerationService.analyze_toxicity')
  def test_orchestrator_regenerates_on_toxic_content(mock_moderation, mock_llm):
      # First attempt is toxic, second is safe
      mock_moderation.side_effect = [0.95, 0.1]
      mock_llm.side_effect = ["Toxic content", "Safe content"]

      orchestrator = ConversationOrchestrator(max_regeneration_attempts=2)
      messages = orchestrator.generate_turn([persona1], "topic", [])

      assert messages[0].message_text == "Safe content"
      assert mock_llm.call_count == 2

  def test_orchestrator_includes_conversation_history():
      orchestrator = ConversationOrchestrator()
      history = [
          {"speaker": "Alice", "message": "I think X"},
          {"speaker": "Bob", "message": "I disagree"}
      ]

      with patch.object(orchestrator.llm_service, 'generate_response') as mock:
          orchestrator.generate_turn([persona1], "topic", history)

          call_args = mock.call_args[0]
          assert history in call_args or any("I think X" in str(arg) for arg in call_args)

  def test_context_window_management():
      # Test that old messages are truncated when context is too long
      orchestrator = ConversationOrchestrator(max_context_tokens=500)
      long_history = [{"speaker": f"P{i}", "message": "Long message " * 50} for i in range(20)]

      messages = orchestrator.generate_turn([persona1], "topic", long_history)

      # Should successfully generate without hitting token limit
      assert len(messages) == 1
  ```

- [ ] **IMPLEMENT:**
  - Create `ConversationOrchestrator` class
  - Method: `generate_turn(personas, topic, history) -> List[Message]`
  - Build context with personality, attitude, history
  - Generate responses via LLM
  - Check moderation
  - Handle regeneration on toxic content
  - Context window management (truncate old messages)

#### 7.3 Conversation UI
- [ ] **WRITE TESTS FIRST (`__tests__/conversations/`):**
  ```typescript
  describe('Conversation View', () => {
    test('displays messages in chronological order', async () => {
      const mockConversation = {
        topic: 'Test topic',
        messages: [
          { persona_name: 'Alice', message_text: 'First message', timestamp: '2024-01-01T00:00:00Z' },
          { persona_name: 'Bob', message_text: 'Second message', timestamp: '2024-01-01T00:01:00Z' }
        ]
      };

      server.use(
        rest.get('/conversations/:id', (req, res, ctx) => res(ctx.json(mockConversation)))
      );

      render(<ConversationView id="abc123" />);

      const messages = await screen.findAllByTestId('message');
      expect(messages[0]).toHaveTextContent('First message');
      expect(messages[1]).toHaveTextContent('Second message');
    });

    test('shows continue button when conversation is active', async () => {
      render(<ConversationView id="abc123" canContinue={true} />);

      expect(screen.getByRole('button', { name: /continue/i })).toBeInTheDocument();
    });

    test('continue button triggers new message generation', async () => {
      const mockContinue = jest.fn();

      render(<ConversationView id="abc123" onContinue={mockContinue} />);

      await userEvent.click(screen.getByRole('button', { name: /continue/i }));

      expect(mockContinue).toHaveBeenCalled();
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    test('displays share link', () => {
      render(<ConversationView id="abc123" />);

      const shareButton = screen.getByRole('button', { name: /share/i });
      expect(shareButton).toBeInTheDocument();
    });
  });

  describe('Conversation Setup', () => {
    test('allows selecting multiple personas', async () => {
      render(<ConversationSetup />);

      await userEvent.click(screen.getByLabelText(/alice/i));
      await userEvent.click(screen.getByLabelText(/bob/i));

      expect(screen.getByText(/2 personas selected/i)).toBeInTheDocument();
    });

    test('requires topic input', async () => {
      render(<ConversationSetup />);

      await userEvent.click(screen.getByRole('button', { name: /start/i }));

      expect(await screen.findByText(/topic is required/i)).toBeInTheDocument();
    });
  });
  ```

- [ ] **IMPLEMENT:**
  - Conversation view page (`/conversations/[id]`)
  - Conversation setup page (`/focus-groups/new`)
  - Public conversation view (`/c/[id]`)
  - Conversation library (`/conversations`)

### Success Criteria:
- **All tests pass** (100%)
- Test coverage > 85% for orchestration logic
- Users can create focus groups with multiple personas
- Personas respond in character
- Conversations are coherent and on-topic
- Conversation pages are shareable
- Users can continue conversations
- E2E test covers full conversation flow

---

## Phase 8: Deployment & CI/CD
**Goal:** Automate deployment to AWS with proper CI/CD pipeline that enforces testing.

### TDD Integration:
- **ALL CI pipelines must run tests and block on failure**
- Test coverage reports must meet minimum thresholds
- No deployment without passing tests

### Deliverables:
- [ ] **GitHub Actions Workflows**
  - `.github/workflows/backend-ci.yml`:
    - **CRITICAL: Tests must pass before proceeding**
    - Lint (flake8, black)
    - Type checking (mypy)
    - **Unit tests (pytest) - BLOCKING**
    - **Coverage check (fail if < 85%)**
    - Build Docker image only if tests pass
  - `.github/workflows/frontend-ci.yml`:
    - Lint (ESLint, Prettier)
    - Type checking (tsc)
    - **Unit tests (Jest) - BLOCKING**
    - **E2E tests (Playwright) - BLOCKING**
    - **Coverage check (fail if < 80%)**
    - Build Next.js app
  - `.github/workflows/deploy.yml`:
    - **Require passing CI before deployment**
    - Deploy to AWS ECS on merge to main
    - Run Terraform apply
    - Push Docker images to ECR
    - Update ECS services
    - Run smoke tests post-deployment

- [ ] **Test Infrastructure in CI**
  - Set up test database containers in CI
  - Configure test environment variables
  - Cache dependencies for faster test runs
  - Parallelize test execution where possible

- [ ] **AWS ECR (Elastic Container Registry)**
  - Create repositories for frontend and backend images
  - Configure lifecycle policies

- [ ] **AWS ECS Configuration**
  - Create ECS cluster
  - Define task definitions (frontend, backend)
  - Configure Fargate launch type
  - Set up service auto-scaling
  - Configure health checks (use `/health` endpoint)

- [ ] **Load Balancer & DNS**
  - Configure Application Load Balancer
  - Set up target groups
  - Configure health checks
  - Set up Route 53 or custom domain

- [ ] **Secrets Management**
  - Store sensitive values in AWS Secrets Manager
  - Configure ECS task IAM roles
  - Inject secrets as environment variables

- [ ] **Environment Configuration**
  - Set up `dev`, `staging`, `prod` environments
  - Configure separate databases for each
  - Implement Terraform workspaces

- [ ] **Monitoring & Logging**
  - Configure CloudWatch Logs
  - Set up log aggregation
  - Create alarms for critical metrics
  - Add alert for test failures in production

### Success Criteria:
- **CI pipeline blocks on test failures** (most important!)
- Test coverage reports are generated and visible
- PRs cannot merge without passing tests
- Merging to main automatically deploys after tests pass
- Application is accessible via custom domain
- Logs are centralized
- Infrastructure is fully defined in Terraform
- Post-deployment smoke tests verify functionality

---

## Phase 9: Comprehensive Testing & Optimization
**Goal:** Fill testing gaps, optimize performance, harden security.

### TDD Perspective:
By this phase, you should have comprehensive tests from Phases 1-7. This phase focuses on:
- **Filling gaps**: Any untested edge cases
- **Load/stress testing**: Non-functional requirements
- **Security testing**: Penetration testing, vulnerability scanning
- **Performance testing**: Under real-world conditions

### Deliverables:

#### 9.1 Testing Gap Analysis & Completion
- [ ] **Backend Testing Audit**
  - Run coverage report: `pytest --cov=app --cov-report=html`
  - Identify gaps (anything < 85% coverage)
  - **Write tests for uncovered code FIRST**
  - Then refactor/fix bugs
  - Target: **90%+ coverage for critical paths**

- [ ] **Frontend Testing Audit**
  - Run coverage report: `npm run test:coverage`
  - Identify gaps
  - **Write missing component/integration tests**
  - Target: **85%+ coverage**

- [ ] **Edge Case Testing**
  ```python
  # Examples of edge cases to test
  def test_persona_with_unicode_name():
      # Test emoji, non-Latin characters
      persona = create_persona(name="测试🎭")
      assert persona.name == "测试🎭"

  def test_conversation_with_single_persona():
      # Edge case: "focus group" of one
      messages = orchestrator.generate_turn([persona1], topic, [])
      assert len(messages) == 1

  def test_extremely_long_topic():
      # What happens with 10,000 character topic?
      topic = "A" * 10000
      with pytest.raises(ValidationError):
          create_conversation(topic=topic, personas=[p1])

  def test_concurrent_persona_creation_same_name():
      # Race condition testing
      pass
  ```

#### 9.2 Load & Performance Testing
- [ ] **Backend Load Tests (Locust or k6)**
  ```python
  # locustfile.py
  class FocusGroupUser(HttpUser):
      @task
      def create_persona(self):
          self.client.post("/personas", json={...})

      @task(3)  # 3x more common
      def view_persona(self):
          self.client.get(f"/personas/{random_id}")

      @task(2)
      def create_conversation(self):
          self.client.post("/conversations", json={...})
  ```
  - Test targets:
    - 1000 concurrent users
    - API response time < 500ms (p95)
    - Database query time < 100ms (p95)

- [ ] **Frontend Performance**
  - Lighthouse CI integration
  - Target scores: Performance 90+, Accessibility 95+, SEO 100
  - Test on slow 3G network
  - Test image loading optimization

#### 9.3 Performance Optimization (Test-Driven)
- [ ] **Database Optimization**
  - **Write test to measure query performance:**
  ```python
  def test_persona_list_query_performance():
      # Create 1000 personas
      personas = [create_persona() for _ in range(1000)]

      import time
      start = time.time()
      result = db.query(Persona).filter_by(user_id=user.id).all()
      duration = time.time() - start

      assert duration < 0.1  # Should complete in < 100ms
  ```
  - **Then optimize:**
    - Add indexes on frequently queried fields
    - Optimize N+1 queries
    - Implement database connection pooling

- [ ] **Caching Layer**
  - **Write test for cache behavior:**
  ```python
  def test_persona_cache_hit():
      persona = get_persona("abc123")  # First call - miss

      with patch.object(db, 'query') as mock_db:
          persona_cached = get_persona("abc123")  # Second call - hit
          mock_db.assert_not_called()  # Should not hit database

      assert persona == persona_cached
  ```
  - **Then implement:**
    - Redis for frequently accessed personas
    - Cache conversation metadata
    - Cache archetype data

- [ ] **LLM Call Optimization**
  - Test and measure token usage
  - Implement prompt compression
  - Consider batch processing for multiple personas

#### 9.4 Security Testing
- [ ] **Automated Security Scans**
  - Dependency scanning (Snyk, Dependabot)
  - OWASP ZAP for penetration testing
  - SQL injection testing
  - XSS testing

- [ ] **Security Hardening Tests**
  ```python
  def test_sql_injection_protection():
      malicious_input = "'; DROP TABLE users; --"
      with pytest.raises(ValidationError):
          create_persona(name=malicious_input)

  def test_rate_limiting_enforced():
      for i in range(100):
          response = client.post("/auth/login", json={...})

      # 101st request should be rate limited
      response = client.post("/auth/login", json={...})
      assert response.status_code == 429

  def test_jwt_expiration_enforced():
      expired_token = create_expired_jwt()
      response = client.get("/personas", headers={"Authorization": f"Bearer {expired_token}"})
      assert response.status_code == 401

  def test_cors_configured_correctly():
      response = client.options("/personas", headers={"Origin": "https://evil.com"})
      assert "evil.com" not in response.headers.get("Access-Control-Allow-Origin", "")
  ```

- [ ] **Implement security measures:**
  - HTTPS enforcement
  - Rate limiting (per-user, per-IP)
  - Input validation and sanitization
  - CORS configuration
  - Security headers (CSP, HSTS, X-Frame-Options)
  - Regular dependency updates

#### 9.5 Database & Infrastructure
- [ ] Add appropriate indexes (test query performance before/after)
- [ ] Set up read replicas
- [ ] Implement connection pooling
- [ ] Add database backups and test restore process

#### 9.6 Documentation
- [ ] Update README with deployment instructions
- [ ] Complete API documentation (Swagger/OpenAPI)
- [ ] Add architecture diagrams
- [ ] Create developer onboarding guide
- [ ] Document testing strategy and how to run tests

### Success Criteria:
- **Test coverage > 90% backend, > 85% frontend**
- **All edge cases covered with tests**
- Page load time < 2 seconds
- API response time < 500ms (p95)
- Zero critical security vulnerabilities
- Application handles 1000+ concurrent users in load tests
- Lighthouse score > 90
- All security tests pass

---

## Phase 10: Polish & Launch Preparation
**Goal:** Final polish, analytics, and launch readiness (with tests!).

### TDD for Features:
Even polish features need tests! Don't skip TDD for "small" features.

### Deliverables:

#### 10.1 Analytics Integration
- [ ] **WRITE TESTS FIRST:**
  ```typescript
  // test_analytics.test.ts
  test('tracks persona creation event', async () => {
    const mockAnalytics = jest.fn();
    global.analytics = { track: mockAnalytics };

    await createPersona({...});

    expect(mockAnalytics).toHaveBeenCalledWith('persona_created', {
      persona_id: expect.any(String),
      attitude: 'Neutral',
      model: 'dalle'
    });
  });
  ```
- [ ] **IMPLEMENT:**
  - Add Google Analytics or PostHog
  - Track key events: persona creation, conversation starts, shares, registration
  - Set up conversion funnels

#### 10.2 User Experience Enhancements
- [ ] **Write tests for UX features:**
  - Test loading skeletons render
  - Test toast notifications appear on actions
  - Test keyboard shortcuts trigger correct actions
  - Test error messages are user-friendly
  - Test onboarding flow progression

- [ ] **IMPLEMENT:**
  - Loading skeletons and optimistic updates
  - Toast notifications
  - Keyboard shortcuts
  - Improved error messages
  - Onboarding flow for new users

#### 10.3 Sharing Optimization
- [ ] **Test Open Graph generation:**
  ```python
  def test_persona_og_image_generation():
      persona = create_persona(name="Alice")
      og_image_url = generate_og_image(persona)

      assert og_image_url.startswith("https://")
      # Verify image exists and is valid
      response = requests.get(og_image_url)
      assert response.status_code == 200
      assert response.headers['Content-Type'].startswith('image/')
  ```

- [ ] **IMPLEMENT:**
  - Generate Open Graph preview images
  - Add social share buttons
  - Implement copy-to-clipboard
  - Create embeddable widgets (stretch)

#### 10.4 Content & Marketing Pages
- [ ] **Test page rendering and SEO:**
  ```typescript
  test('landing page renders hero section', () => {
    render(<LandingPage />);
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  test('landing page has proper meta tags', () => {
    render(<LandingPage />);
    const metaDescription = document.querySelector('meta[name="description"]');
    expect(metaDescription).toHaveAttribute('content', expect.stringContaining('AI Focus Groups'));
  });
  ```

- [ ] **IMPLEMENT:**
  - Landing page
  - About page
  - FAQ page
  - Terms of Service and Privacy Policy
  - Blog (optional)

#### 10.5 Admin Tools
- [ ] **Test admin functionality:**
  ```python
  def test_admin_dashboard_access_control(client, user_headers, admin_headers):
      # Regular user cannot access admin dashboard
      response = client.get("/admin/dashboard", headers=user_headers)
      assert response.status_code == 403

      # Admin can access
      response = client.get("/admin/dashboard", headers=admin_headers)
      assert response.status_code == 200

  def test_admin_can_ban_user(client, admin_headers):
      response = client.post("/admin/users/123/ban", headers=admin_headers)
      assert response.status_code == 200

      # Verify banned user cannot login
      banned_user_response = client.post("/auth/login", json={...})
      assert banned_user_response.status_code == 403
  ```

- [ ] **IMPLEMENT:**
  - Admin dashboard
  - User management (ban, delete)
  - Content moderation review queue
  - Analytics overview

#### 10.6 Cost Optimization
- [ ] Test usage quota enforcement:
  ```python
  def test_user_quota_enforcement():
      user = create_user(quota_limit=10)

      # Create 10 personas - should succeed
      for i in range(10):
          create_persona(user=user)

      # 11th persona should fail
      with pytest.raises(QuotaExceededError):
          create_persona(user=user)
  ```

- [ ] **IMPLEMENT:**
  - Review and optimize LLM API costs
  - Implement usage quotas per user
  - Add billing/subscription system (if monetizing)
  - Monitor AWS costs

#### 10.7 Launch Checklist
- [ ] **Pre-Launch Testing:**
  - [ ] Run full test suite (backend, frontend, E2E)
  - [ ] Verify test coverage meets targets (>85%)
  - [ ] Run load tests simulating launch traffic
  - [ ] Test disaster recovery procedures
  - [ ] Test backup and restore
  - [ ] Verify monitoring and alerting work

- [ ] **Infrastructure:**
  - [ ] Domain registered and configured
  - [ ] SSL certificates active
  - [ ] CDN configured (CloudFront)
  - [ ] Database backups automated
  - [ ] Monitoring dashboards set up

- [ ] **Business:**
  - [ ] Support email/system set up
  - [ ] Legal pages live (ToS, Privacy Policy)
  - [ ] Social media accounts created
  - [ ] Launch blog post written
  - [ ] Press kit prepared

- [ ] **Final Smoke Tests (Production):**
  ```python
  # smoke_tests.py - Run against production after deployment
  def test_production_health_check():
      response = requests.get("https://aifocusgroups.com/health")
      assert response.status_code == 200

  def test_production_persona_creation_works():
      # Create test account
      # Create test persona
      # Verify it appears in database
      # Clean up test data
      pass
  ```

### Success Criteria:
- **All new features have tests**
- **Full test suite passes in production**
- All user-facing features are polished and intuitive
- Sharing generates attractive previews on social media
- Analytics are tracking correctly
- Load tests simulate expected launch traffic
- Application is ready for public launch
- Cost projections are reasonable
- Support system is ready for user inquiries

---

## TDD Daily Workflow

### Morning Routine (Start of Development Day):
1. **Pull latest code and run tests:**
   ```bash
   git pull origin main
   # Backend
   cd backend && pytest
   # Frontend
   cd frontend && npm test
   ```
2. **All tests must pass before starting new work**
3. **Review which feature you're implementing today**
4. **Identify the first test case to write**

### Development Cycle (Repeat for each feature):
1. **RED: Write a failing test**
   - Think: "What behavior do I want?"
   - Write test that describes the behavior
   - Run test - it should FAIL
   - If it passes without implementation, the test is wrong!

2. **GREEN: Write minimal code to pass**
   - Don't over-engineer
   - Hardcode values if needed (will refactor later)
   - Just make it pass

3. **REFACTOR: Clean up**
   - Improve code quality
   - Remove duplication
   - Extract functions/classes
   - Tests must still pass!

4. **Commit:**
   ```bash
   git add .
   git commit -m "feat: add persona weight calculation with tests"
   ```

### End of Day Routine:
1. **Run full test suite:**
   ```bash
   # Backend
   pytest --cov=app --cov-report=html
   # Frontend
   npm run test:coverage
   ```
2. **Check coverage reports - look for gaps**
3. **All tests must pass before pushing**
4. **Push to remote:**
   ```bash
   git push origin feature/persona-vector-engine
   ```

### Code Review Checklist:
- [ ] Does the PR include tests for all new code?
- [ ] Are tests written BEFORE implementation? (Check git history)
- [ ] Do all tests pass in CI?
- [ ] Is coverage maintained or improved?
- [ ] Are tests clear and well-named?
- [ ] Are edge cases covered?

---

## Common TDD Challenges & Solutions

### Challenge 1: "I don't know how to test this yet"
**Solution:** Write a high-level test first, even if it's wrong
```python
# Start with this, even if you don't know the implementation
def test_personality_calculator_works():
    calculator = PersonalityCalculator()
    result = calculator.calculate_personality_weights(x=0.5, y=0.5)
    # I don't know what result should be yet, but I'll figure it out
    assert result is not None
```
As you learn the requirements, refine the test.

### Challenge 2: "Testing external APIs is slow/expensive"
**Solution:** Use mocks and dependency injection
```python
# Don't do this (slow, expensive):
def test_llm_generation():
    result = openai.ChatCompletion.create(...)  # Actual API call

# Do this (fast, free):
@patch('openai.ChatCompletion.create')
def test_llm_generation(mock_openai):
    mock_openai.return_value = {"choices": [{"message": {"content": "Test"}}]}
    result = llm_service.generate_motto({...})
    assert result == "Test"
```

### Challenge 3: "My tests are brittle and break often"
**Solution:** Test behavior, not implementation
```python
# Brittle (tests implementation details):
def test_persona_creation():
    persona = create_persona(...)
    assert persona._internal_state == "initialized"  # Too specific!

# Better (tests behavior):
def test_persona_creation():
    persona = create_persona(name="Alice", age=30)
    assert persona.name == "Alice"
    assert persona.age == 30
    assert persona.id is not None  # Has been saved
```

### Challenge 4: "TDD slows me down"
**Initial learning curve:** Yes, TDD is slower at first (2-4 weeks to become proficient)

**After proficiency:** TDD is FASTER because:
- Fewer bugs to fix later
- Easier refactoring (tests catch breaks)
- Less debugging time (tests pinpoint issues)
- Faster code review (reviewers trust tested code)

**Tip:** Start with simple tests, increase complexity gradually

### Challenge 5: "I need to explore/prototype first"
**Solution:** Spike then throw away
```
1. Write exploratory code (no tests) in a separate branch
2. Understand the problem/solution
3. Delete the exploratory code
4. Start over with TDD, using knowledge from exploration
```
This is acceptable! Exploration !== Production code.

### Challenge 6: "Legacy code has no tests"
**Solution:** Test new code, gradually add tests to old code
```
1. All NEW code must be tested (no exceptions)
2. When modifying old code:
   a. Write tests for the section you're changing
   b. Then make your changes
   c. Gradually increase coverage
```

---

## TDD Best Practices for This Project

### 1. Test Naming Conventions
Use descriptive names that explain the behavior:

**Backend (Python):**
```python
# Good
def test_persona_creation_generates_unique_six_character_id():
def test_calculate_personality_weights_returns_normalized_dict():
def test_conversation_orchestrator_regenerates_on_toxic_content():

# Bad
def test_persona():
def test_weights():
def test_orchestrator():
```

**Frontend (TypeScript):**
```typescript
// Good
test('personality grid updates preview when user clicks new position', ...)
test('persona creation form shows validation error for empty name', ...)

// Bad
test('grid works', ...)
test('form validates', ...)
```

### 2. Test Organization
Mirror your source code structure:

```
backend/
  app/
    services/
      personality_calculator.py
  tests/
    services/
      test_personality_calculator.py  # Same structure!

frontend/
  components/
    PersonalityGrid.tsx
  __tests__/
    components/
      PersonalityGrid.test.tsx  # Same structure!
```

### 3. Use Fixtures and Factories
Don't repeat test data setup:

```python
# conftest.py (pytest fixtures)
@pytest.fixture
def test_user(db_session):
    user = User(email="test@example.com", password_hash="...")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_persona(db_session, test_user):
    persona = Persona(
        user_id=test_user.id,
        name="Test Persona",
        unique_id="abc123",
        ...
    )
    db_session.add(persona)
    db_session.commit()
    return persona

# Now use in tests:
def test_persona_deletion(test_persona, db_session):
    delete_persona(test_persona.id)
    assert db_session.query(Persona).filter_by(id=test_persona.id).first() is None
```

### 4. Test Coverage Targets by Code Type
- **Business logic (vector math, orchestration):** 95%+
- **API endpoints:** 90%+
- **Database models:** 85%+
- **Frontend components:** 80%+
- **Utility functions:** 90%+
- **Configuration/setup code:** 60%+ (acceptable to be lower)

### 5. When to Skip TDD
Rare exceptions where TDD may not apply:
- **Infrastructure code** (Terraform, Docker configs) - test manually
- **One-off scripts** - not production code
- **Prototypes/spikes** - throw away code
- **Visual design** - requires manual review

For EVERYTHING else: TDD is required.

### 6. Test Data Management
- Use factories (factory_boy for Python, factory-bot for JS)
- Create minimal test data (don't create unnecessary objects)
- Clean up after tests (use fixtures that auto-cleanup)
- Use in-memory databases for speed where possible

### 7. Continuous Testing During Development
Keep tests running in watch mode:

```bash
# Backend - auto-run tests on file change
ptw  # pytest-watch

# Frontend - auto-run tests on file change
npm test -- --watch
```

This gives instant feedback as you code!

---

## Appendix A: Technical Considerations

### Database Schema (Simplified)
```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Personas
CREATE TABLE personas (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    unique_id VARCHAR(6) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(50),
    description TEXT,
    attitude VARCHAR(50),
    model_used VARCHAR(50),
    personality_vector JSONB,
    motto TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    unique_id VARCHAR(6) UNIQUE NOT NULL,
    topic TEXT NOT NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversation Participants
CREATE TABLE conversation_participants (
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    persona_id INTEGER REFERENCES personas(id) ON DELETE CASCADE,
    PRIMARY KEY (conversation_id, persona_id)
);

-- Conversation Messages
CREATE TABLE conversation_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    persona_id INTEGER REFERENCES personas(id),
    message_text TEXT NOT NULL,
    toxicity_score FLOAT,
    moderation_status VARCHAR(50) DEFAULT 'approved',
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### Environment Variables Template
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_focus_groups
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# LLM Provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Image Generation
DALLE_API_KEY=...
OPENJOURNEY_API_URL=...

# Moderation
OPENAI_MODERATION_API_KEY=sk-...
TOXICITY_THRESHOLD=0.7

# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=...
S3_BUCKET_NAME=ai-focus-groups-avatars

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GA_ID=G-...
```

---

## Appendix B: Research & Academic Validation
To validate the unique value proposition, research these topics:
- **"Synthetic Participants in Focus Groups"** - Academic literature on AI personas in qualitative research
- **"Personality Modeling in AI Systems"** - Research on computational personality models
- **"Distributed Cognition and Multi-Agent Systems"** - Theoretical framework for AI conversations
- **"Representativeness in AI-Generated Opinions"** - Studies on bias and diversity in synthetic data

Potential papers:
- "Can Language Models Replace Human Participants?" (Park et al., 2023)
- "Personality-Driven Social Networks" (Jiang et al., 2022)
- "Synthetic Respondents: A New Frontier in Social Science" (Argyle et al., 2022)

---

## Appendix C: Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLM API costs spiral | High | Implement per-user quotas, caching, model selection |
| Content moderation fails | Critical | Multiple layers: AI moderation + user reporting + admin review |
| Performance issues with concurrent conversations | Medium | Implement job queues, optimize database queries, scale horizontally |
| Low user adoption | High | Focus on shareability, SEO optimization, compelling landing page |
| Legal issues (ToS, GDPR) | High | Consult legal expert, implement data deletion, clear ToS |

---

## Next Steps

### Immediate Actions:
1. **Review this plan** with stakeholders and team
2. **Prioritize phases** based on business goals
   - Note: Some phases can be parallelized (e.g., frontend/backend development)
3. **Team Training on TDD** (if needed)
   - Schedule TDD workshop or pair programming sessions
   - Review TDD best practices in this document
   - Practice on a simple feature first
4. **Set up project management** (Jira, Linear, GitHub Projects)
   - Create tickets for each phase
   - Link tickets to test coverage requirements
5. **Establish TDD Policy:**
   - All PRs require tests
   - Code review checklist includes test verification
   - CI pipeline blocks on test failures
   - Coverage thresholds enforced

### Week 1 Goals:
- [ ] Complete Phase 1: Infrastructure & Scaffolding
- [ ] Set up testing infrastructure (pytest, Jest, CI)
- [ ] Verify docker-compose works locally
- [ ] Team members can run tests locally
- [ ] First TDD cycle completed (even if just a simple function)

### Success Metrics:
Track these throughout development:
- **Test coverage:** Backend >90%, Frontend >85%
- **Test execution time:** Keep under 5 minutes for full suite
- **Bug count:** Should decrease over time with TDD
- **Code review time:** Should decrease (trusted tests)
- **Deployment confidence:** Should increase (test safety net)

---

## Final Reminder: TDD is Non-Negotiable

This project **REQUIRES** Test-Driven Development. This is not optional or a "nice to have."

### Why TDD is Critical for This Project:
1. **Complex AI Integration:** LLM behavior is unpredictable - tests ensure consistency
2. **Mathematical Correctness:** Vector calculations must be precise - tests verify accuracy
3. **Content Moderation:** Safety critical - must be thoroughly tested
4. **Shareability:** Public URLs mean bugs are visible to world - tests prevent embarrassment
5. **Cost Control:** LLM APIs are expensive - tests help optimize without breaking functionality
6. **Team Onboarding:** Tests serve as executable documentation for junior developers

### The TDD Commitment:
Every team member commits to:
- ✅ Write tests BEFORE implementation
- ✅ Never skip tests "just this once"
- ✅ Maintain or improve coverage with every PR
- ✅ Review tests as carefully as implementation code
- ✅ Run full test suite before pushing code

**Remember:**
> "Legacy code is code without tests." - Michael Feathers

Don't create legacy code from day one. Start with tests.

---

**Document Version:** 2.0 (Updated with TDD requirements)
**Last Updated:** 2026-01-31
**Author:** Claude Sonnet 4.5
