"""
AI Focus Groups - Backend Test Suite

This package contains all tests for the backend application,
organized following TDD principles.

Test Organization:
- unit/: Fast, isolated unit tests for individual functions and classes
- integration/: Tests for API endpoints, database interactions
- fixtures/: Shared test data and setup utilities

All tests should:
1. Be written BEFORE implementation code (TDD)
2. Run fast (< 5 seconds for entire suite initially)
3. Be isolated (no dependencies between tests)
4. Use mocks for external services (LLM APIs, image generation)
5. Have descriptive names that explain what they test

Run tests with: pytest
Run with coverage: pytest --cov=app
Run specific tests: pytest -m unit  # or -m integration
"""
