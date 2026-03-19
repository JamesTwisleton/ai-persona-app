"""
Moderation Model Tests - Phase 5 (RED phase)

Tests for ModerationAuditLog database model.

TDD: These tests are written FIRST. They define expected behavior.
"""

import pytest
from datetime import datetime


class TestModerationAuditLog:
    """Tests for the ModerationAuditLog database model."""

    def test_create_audit_log(self, db_session):
        from app.models.moderation import ModerationAuditLog
        log = ModerationAuditLog(
            content="Some flagged content",
            toxicity_score=0.87,
            source="persona_description",
            source_id="abc123",
            action_taken="blocked",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        assert log.id is not None
        assert log.content == "Some flagged content"
        assert log.toxicity_score == pytest.approx(0.87)
        assert log.source == "persona_description"
        assert log.source_id == "abc123"
        assert log.action_taken == "blocked"

    def test_created_at_auto_set(self, db_session):
        from app.models.moderation import ModerationAuditLog
        log = ModerationAuditLog(
            content="Test",
            toxicity_score=0.9,
            source="test",
            source_id="x",
            action_taken="blocked",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        assert log.created_at is not None

    def test_default_action_taken_is_pending(self, db_session):
        from app.models.moderation import ModerationAuditLog
        log = ModerationAuditLog(
            content="Borderline content",
            toxicity_score=0.75,
            source="persona_description",
            source_id="def456",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        assert log.action_taken == "pending"

    def test_reviewed_by_is_nullable(self, db_session):
        from app.models.moderation import ModerationAuditLog
        log = ModerationAuditLog(
            content="Test",
            toxicity_score=0.8,
            source="test",
            source_id="x",
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        assert log.reviewed_by is None

    def test_multiple_logs_can_exist(self, db_session):
        from app.models.moderation import ModerationAuditLog
        for i in range(3):
            log = ModerationAuditLog(
                content=f"Content {i}",
                toxicity_score=0.8 + i * 0.05,
                source="test",
                source_id=str(i),
            )
            db_session.add(log)
        db_session.commit()

        logs = db_session.query(ModerationAuditLog).all()
        assert len(logs) == 3

    def test_repr(self, db_session):
        from app.models.moderation import ModerationAuditLog
        log = ModerationAuditLog(
            content="Test content",
            toxicity_score=0.85,
            source="persona_description",
            source_id="abc",
        )
        db_session.add(log)
        db_session.commit()
        assert "ModerationAuditLog" in repr(log) or "0.85" in repr(log)


class TestUserIsAdmin:
    """Tests for is_admin field on User model."""

    def test_user_is_not_admin_by_default(self, db_session):
        from app.models.user import User
        user = User(
            email="regular@example.com",
            google_id="google_regular_1",
            name="Regular User",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        assert user.is_admin is False

    def test_user_can_be_made_admin(self, db_session):
        from app.models.user import User
        user = User(
            email="admin@example.com",
            google_id="google_admin_1",
            name="Admin User",
            is_admin=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        assert user.is_admin is True
