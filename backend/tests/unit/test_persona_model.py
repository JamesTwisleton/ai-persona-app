"""
Persona Model Tests - Phase 3B

TDD Phase: RED - These tests are written BEFORE the Persona model exists.

Tests cover:
- Persona creation with basic fields
- OCEAN score storage and validation
- Relationship to User model
- Unique ID generation
- Serialization to dict
- Database constraints
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import IntegrityError

from app.database import Base
from app.models.user import User


class TestPersonaModelCreation:
    """Test basic Persona model instantiation and field storage."""

    def test_persona_can_be_created_with_required_fields(self, db_session):
        """Persona can be created with minimal required fields."""
        from app.models.persona import Persona

        user = User(email="test@example.com", google_id="google_123")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Alice",
            ocean_openness=0.8,
            ocean_conscientiousness=0.6,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.7,
            ocean_neuroticism=0.3,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert persona.id is not None
        assert persona.name == "Alice"
        assert persona.user_id == user.id

    def test_persona_stores_ocean_scores(self, db_session):
        """All five OCEAN dimensions are stored and retrieved correctly."""
        from app.models.persona import Persona

        user = User(email="ocean@example.com", google_id="google_ocean")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="OCEAN Test",
            ocean_openness=0.9,
            ocean_conscientiousness=0.8,
            ocean_extraversion=0.7,
            ocean_agreeableness=0.6,
            ocean_neuroticism=0.5,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert persona.ocean_openness == pytest.approx(0.9)
        assert persona.ocean_conscientiousness == pytest.approx(0.8)
        assert persona.ocean_extraversion == pytest.approx(0.7)
        assert persona.ocean_agreeableness == pytest.approx(0.6)
        assert persona.ocean_neuroticism == pytest.approx(0.5)

    def test_persona_stores_optional_fields(self, db_session):
        """Optional fields (age, gender, description, attitude) are stored correctly."""
        from app.models.persona import Persona

        user = User(email="optional@example.com", google_id="google_opt")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Bob",
            age=35,
            gender="Male",
            description="A thoughtful analyst who loves data",
            attitude="Neutral",
            ocean_openness=0.5,
            ocean_conscientiousness=0.7,
            ocean_extraversion=0.4,
            ocean_agreeableness=0.6,
            ocean_neuroticism=0.3,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert persona.age == 35
        assert persona.gender == "Male"
        assert persona.description == "A thoughtful analyst who loves data"
        assert persona.attitude == "Neutral"

    def test_persona_stores_archetype_affinities_as_json(self, db_session):
        """Archetype affinities are stored as JSON and retrieved correctly."""
        from app.models.persona import Persona

        user = User(email="affinity@example.com", google_id="google_aff")
        db_session.add(user)
        db_session.flush()

        affinities = {
            "THE_ANALYST": 0.85,
            "THE_SKEPTIC": 0.60,
            "THE_PRAGMATIST": 0.40,
        }

        persona = Persona(
            user_id=user.id,
            name="Carol",
            ocean_openness=0.7,
            ocean_conscientiousness=0.9,
            ocean_extraversion=0.25,
            ocean_agreeableness=0.35,
            ocean_neuroticism=0.2,
            archetype_affinities=affinities,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert persona.archetype_affinities["THE_ANALYST"] == pytest.approx(0.85)
        assert persona.archetype_affinities["THE_SKEPTIC"] == pytest.approx(0.60)

    def test_persona_stores_avatar_and_motto(self, db_session):
        """Avatar URL and motto fields are stored correctly."""
        from app.models.persona import Persona

        user = User(email="motto@example.com", google_id="google_motto")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Diana",
            ocean_openness=0.6,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.8,
            ocean_agreeableness=0.8,
            ocean_neuroticism=0.2,
            motto="Carpe diem",
            avatar_url="https://example.com/avatar/diana.png",
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert persona.motto == "Carpe diem"
        assert persona.avatar_url == "https://example.com/avatar/diana.png"

    def test_persona_has_timestamps(self, db_session):
        """Persona has created_at and updated_at timestamps."""
        from app.models.persona import Persona

        user = User(email="ts@example.com", google_id="google_ts")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Eve",
            ocean_openness=0.5,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.5,
            ocean_neuroticism=0.5,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert persona.created_at is not None
        assert persona.updated_at is not None


class TestPersonaUniqueId:
    """Test unique_id generation for personas."""

    def test_persona_has_unique_id_after_creation(self, db_session):
        """Persona gets a unique_id auto-generated on creation."""
        from app.models.persona import Persona

        user = User(email="uid@example.com", google_id="google_uid")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Frank",
            ocean_openness=0.5,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.5,
            ocean_neuroticism=0.5,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert persona.unique_id is not None
        assert len(persona.unique_id) == 6
        assert persona.unique_id.isalnum()

    def test_two_personas_have_different_unique_ids(self, db_session):
        """Each persona gets a distinct unique_id."""
        from app.models.persona import Persona

        user = User(email="uid2@example.com", google_id="google_uid2")
        db_session.add(user)
        db_session.flush()

        persona1 = Persona(
            user_id=user.id,
            name="P1",
            ocean_openness=0.5,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.5,
            ocean_neuroticism=0.5,
        )
        persona2 = Persona(
            user_id=user.id,
            name="P2",
            ocean_openness=0.6,
            ocean_conscientiousness=0.6,
            ocean_extraversion=0.6,
            ocean_agreeableness=0.6,
            ocean_neuroticism=0.4,
        )
        db_session.add_all([persona1, persona2])
        db_session.commit()

        assert persona1.unique_id != persona2.unique_id

    def test_unique_id_enforces_uniqueness_constraint(self, db_session):
        """Two personas cannot share the same unique_id."""
        from app.models.persona import Persona

        user = User(email="uid3@example.com", google_id="google_uid3")
        db_session.add(user)
        db_session.flush()

        persona1 = Persona(
            user_id=user.id,
            name="P1",
            unique_id="abc123",
            ocean_openness=0.5,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.5,
            ocean_neuroticism=0.5,
        )
        persona2 = Persona(
            user_id=user.id,
            name="P2",
            unique_id="abc123",  # Duplicate
            ocean_openness=0.5,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.5,
            ocean_neuroticism=0.5,
        )
        db_session.add(persona1)
        db_session.flush()
        db_session.add(persona2)

        with pytest.raises(IntegrityError):
            db_session.flush()


class TestPersonaRelationships:
    """Test Persona relationships with User."""

    def test_persona_belongs_to_user(self, db_session):
        """Persona has a foreign key relationship to User."""
        from app.models.persona import Persona

        user = User(email="rel@example.com", google_id="google_rel")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="George",
            ocean_openness=0.5,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.5,
            ocean_neuroticism=0.5,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert persona.user_id == user.id

    def test_user_can_have_multiple_personas(self, db_session):
        """One user can own many personas."""
        from app.models.persona import Persona

        user = User(email="multi@example.com", google_id="google_multi")
        db_session.add(user)
        db_session.flush()

        for i in range(3):
            p = Persona(
                user_id=user.id,
                name=f"Persona {i}",
                ocean_openness=0.5,
                ocean_conscientiousness=0.5,
                ocean_extraversion=0.5,
                ocean_agreeableness=0.5,
                ocean_neuroticism=0.5,
            )
            db_session.add(p)

        db_session.commit()

        count = db_session.query(Persona).filter_by(user_id=user.id).count()
        assert count == 3

    def test_persona_requires_valid_user_id(self, db_session):
        """Persona cannot be created with a non-existent user_id."""
        from app.models.persona import Persona

        persona = Persona(
            user_id=99999,  # Non-existent
            name="Orphan",
            ocean_openness=0.5,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.5,
            ocean_neuroticism=0.5,
        )
        db_session.add(persona)

        with pytest.raises(IntegrityError):
            db_session.flush()


class TestPersonaSerialization:
    """Test Persona.to_dict() serialization."""

    def test_to_dict_returns_all_fields(self, db_session):
        """to_dict() includes all expected keys."""
        from app.models.persona import Persona

        user = User(email="serial@example.com", google_id="google_serial")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Helen",
            age=28,
            gender="Female",
            description="An empathetic activist",
            attitude="Comical",
            ocean_openness=0.8,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.7,
            ocean_agreeableness=0.85,
            ocean_neuroticism=0.25,
            motto="Change the world",
            avatar_url="https://example.com/helen.png",
            archetype_affinities={"THE_ACTIVIST": 0.9},
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        result = persona.to_dict()

        assert "id" in result
        assert "unique_id" in result
        assert "user_id" in result
        assert "name" in result
        assert "age" in result
        assert "gender" in result
        assert "description" in result
        assert "attitude" in result
        assert "ocean_openness" in result
        assert "ocean_conscientiousness" in result
        assert "ocean_extraversion" in result
        assert "ocean_agreeableness" in result
        assert "ocean_neuroticism" in result
        assert "archetype_affinities" in result
        assert "motto" in result
        assert "avatar_url" in result
        assert "created_at" in result

    def test_to_dict_ocean_scores_as_floats(self, db_session):
        """OCEAN scores in to_dict() are floats."""
        from app.models.persona import Persona

        user = User(email="float@example.com", google_id="google_float")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Ivan",
            ocean_openness=0.75,
            ocean_conscientiousness=0.55,
            ocean_extraversion=0.45,
            ocean_agreeableness=0.65,
            ocean_neuroticism=0.35,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        result = persona.to_dict()

        assert isinstance(result["ocean_openness"], float)
        assert result["ocean_openness"] == pytest.approx(0.75)

    def test_repr_shows_name_and_unique_id(self, db_session):
        """__repr__ shows name and unique_id for debugging."""
        from app.models.persona import Persona

        user = User(email="repr@example.com", google_id="google_repr")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Julia",
            ocean_openness=0.5,
            ocean_conscientiousness=0.5,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.5,
            ocean_neuroticism=0.5,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        assert "Julia" in repr(persona)
        assert persona.unique_id in repr(persona)


class TestPersonaOceanVector:
    """Test OCEAN vector extraction from Persona."""

    def test_get_ocean_vector_returns_dict(self, db_session):
        """get_ocean_vector() returns a dict with 5 OCEAN keys."""
        from app.models.persona import Persona

        user = User(email="vec@example.com", google_id="google_vec")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Kate",
            ocean_openness=0.8,
            ocean_conscientiousness=0.6,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.7,
            ocean_neuroticism=0.3,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        vector = persona.get_ocean_vector()

        assert isinstance(vector, dict)
        assert set(vector.keys()) == {"O", "C", "E", "A", "N"}
        assert vector["O"] == pytest.approx(0.8)
        assert vector["C"] == pytest.approx(0.6)
        assert vector["E"] == pytest.approx(0.5)
        assert vector["A"] == pytest.approx(0.7)
        assert vector["N"] == pytest.approx(0.3)

    def test_all_ocean_values_in_valid_range(self, db_session):
        """All OCEAN scores from get_ocean_vector() are between 0 and 1."""
        from app.models.persona import Persona

        user = User(email="range@example.com", google_id="google_range")
        db_session.add(user)
        db_session.flush()

        persona = Persona(
            user_id=user.id,
            name="Leo",
            ocean_openness=0.0,
            ocean_conscientiousness=1.0,
            ocean_extraversion=0.5,
            ocean_agreeableness=0.25,
            ocean_neuroticism=0.75,
        )
        db_session.add(persona)
        db_session.commit()
        db_session.refresh(persona)

        vector = persona.get_ocean_vector()

        for code, value in vector.items():
            assert 0.0 <= value <= 1.0, f"{code} = {value} is out of range"
