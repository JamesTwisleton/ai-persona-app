"""
Unit tests for OCEAN Trait System (Phase 3A)

Following TDD approach - these tests are written FIRST before implementation.

Tests cover:
- Trait dataclass validation
- TraitRegistry returns exactly 5 OCEAN traits
- PersonalityVector initialization and operations
"""

import pytest
import numpy as np
from app.models.traits import Trait, TraitRegistry, PersonalityVector


class TestTrait:
    """Test the Trait dataclass"""

    def test_trait_creation(self):
        """Test creating a valid Trait"""
        trait = Trait(
            code="O",
            name="Openness",
            description="Openness to experience",
            low_label="Conventional",
            high_label="Creative",
            category="psychological"
        )

        assert trait.code == "O"
        assert trait.name == "Openness"
        assert trait.description == "Openness to experience"
        assert trait.low_label == "Conventional"
        assert trait.high_label == "Creative"
        assert trait.category == "psychological"

    def test_trait_immutability(self):
        """Test that Trait is frozen (immutable)"""
        trait = Trait(
            code="O",
            name="Openness",
            description="Test",
            low_label="Low",
            high_label="High",
            category="psychological"
        )

        # Should raise error when trying to modify
        with pytest.raises(AttributeError):
            trait.code = "C"


class TestTraitRegistry:
    """Test the TraitRegistry class"""

    def test_registry_has_ocean_traits(self):
        """Test that registry contains all 5 OCEAN traits"""
        assert hasattr(TraitRegistry, 'OPENNESS')
        assert hasattr(TraitRegistry, 'CONSCIENTIOUSNESS')
        assert hasattr(TraitRegistry, 'EXTRAVERSION')
        assert hasattr(TraitRegistry, 'AGREEABLENESS')
        assert hasattr(TraitRegistry, 'NEUROTICISM')

    def test_get_active_traits_returns_five(self):
        """Test that get_active_traits() returns exactly 5 traits"""
        active_traits = TraitRegistry.get_active_traits()

        assert len(active_traits) == 5
        assert all(isinstance(trait, Trait) for trait in active_traits)

    def test_ocean_trait_codes(self):
        """Test that OCEAN traits have correct codes"""
        active_traits = TraitRegistry.get_active_traits()
        trait_codes = [trait.code for trait in active_traits]

        assert "O" in trait_codes
        assert "C" in trait_codes
        assert "E" in trait_codes
        assert "A" in trait_codes
        assert "N" in trait_codes

    def test_trait_order_is_ocean(self):
        """Test that traits are returned in O-C-E-A-N order"""
        active_traits = TraitRegistry.get_active_traits()
        expected_codes = ["O", "C", "E", "A", "N"]
        actual_codes = [trait.code for trait in active_traits]

        assert actual_codes == expected_codes

    def test_openness_trait_properties(self):
        """Test Openness trait has correct properties"""
        assert TraitRegistry.OPENNESS.code == "O"
        assert TraitRegistry.OPENNESS.name == "Openness"
        assert TraitRegistry.OPENNESS.category == "psychological"
        assert len(TraitRegistry.OPENNESS.description) > 0
        assert len(TraitRegistry.OPENNESS.low_label) > 0
        assert len(TraitRegistry.OPENNESS.high_label) > 0

    def test_all_traits_have_psychological_category(self):
        """Test that all OCEAN traits are categorized as psychological"""
        active_traits = TraitRegistry.get_active_traits()

        for trait in active_traits:
            assert trait.category == "psychological"


class TestPersonalityVector:
    """Test the PersonalityVector class"""

    def test_personality_vector_creation(self):
        """Test creating a PersonalityVector with valid OCEAN scores"""
        trait_values = {
            "O": 0.7,
            "C": 0.5,
            "E": 0.8,
            "A": 0.6,
            "N": 0.3
        }

        pv = PersonalityVector(trait_values)

        assert pv.vector.shape == (5,)
        assert np.allclose(pv.vector, [0.7, 0.5, 0.8, 0.6, 0.3])

    def test_personality_vector_validation_min(self):
        """Test that values below 0.0 raise ValueError"""
        trait_values = {
            "O": -0.1,  # Invalid: below 0
            "C": 0.5,
            "E": 0.8,
            "A": 0.6,
            "N": 0.3
        }

        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            PersonalityVector(trait_values)

    def test_personality_vector_validation_max(self):
        """Test that values above 1.0 raise ValueError"""
        trait_values = {
            "O": 0.7,
            "C": 1.5,  # Invalid: above 1.0
            "E": 0.8,
            "A": 0.6,
            "N": 0.3
        }

        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            PersonalityVector(trait_values)

    def test_personality_vector_missing_trait(self):
        """Test that missing trait raises ValueError"""
        trait_values = {
            "O": 0.7,
            "C": 0.5,
            # Missing "E"
            "A": 0.6,
            "N": 0.3
        }

        with pytest.raises(ValueError, match="Missing required trait"):
            PersonalityVector(trait_values)

    def test_euclidean_distance_same_vector(self):
        """Test Euclidean distance between identical vectors is 0"""
        trait_values = {
            "O": 0.7,
            "C": 0.5,
            "E": 0.8,
            "A": 0.6,
            "N": 0.3
        }

        pv1 = PersonalityVector(trait_values)
        pv2 = PersonalityVector(trait_values)

        distance = pv1.euclidean_distance(pv2)

        assert distance == pytest.approx(0.0, abs=1e-10)

    def test_euclidean_distance_opposite_vectors(self):
        """Test Euclidean distance between opposite vectors"""
        trait_values_1 = {
            "O": 0.0,
            "C": 0.0,
            "E": 0.0,
            "A": 0.0,
            "N": 0.0
        }

        trait_values_2 = {
            "O": 1.0,
            "C": 1.0,
            "E": 1.0,
            "A": 1.0,
            "N": 1.0
        }

        pv1 = PersonalityVector(trait_values_1)
        pv2 = PersonalityVector(trait_values_2)

        distance = pv1.euclidean_distance(pv2)

        # sqrt(5) ≈ 2.236
        expected = np.sqrt(5)
        assert distance == pytest.approx(expected, abs=1e-6)

    def test_euclidean_distance_is_symmetric(self):
        """Test that distance(A, B) == distance(B, A)"""
        trait_values_1 = {
            "O": 0.2,
            "C": 0.8,
            "E": 0.5,
            "A": 0.7,
            "N": 0.4
        }

        trait_values_2 = {
            "O": 0.9,
            "C": 0.3,
            "E": 0.1,
            "A": 0.6,
            "N": 0.8
        }

        pv1 = PersonalityVector(trait_values_1)
        pv2 = PersonalityVector(trait_values_2)

        distance_1_2 = pv1.euclidean_distance(pv2)
        distance_2_1 = pv2.euclidean_distance(pv1)

        assert distance_1_2 == pytest.approx(distance_2_1)

    def test_get_trait_value(self):
        """Test retrieving individual trait values"""
        trait_values = {
            "O": 0.7,
            "C": 0.5,
            "E": 0.8,
            "A": 0.6,
            "N": 0.3
        }

        pv = PersonalityVector(trait_values)

        assert pv.get_trait_value("O") == pytest.approx(0.7)
        assert pv.get_trait_value("C") == pytest.approx(0.5)
        assert pv.get_trait_value("E") == pytest.approx(0.8)
        assert pv.get_trait_value("A") == pytest.approx(0.6)
        assert pv.get_trait_value("N") == pytest.approx(0.3)

    def test_get_trait_value_invalid_code(self):
        """Test that getting invalid trait code raises ValueError"""
        trait_values = {
            "O": 0.7,
            "C": 0.5,
            "E": 0.8,
            "A": 0.6,
            "N": 0.3
        }

        pv = PersonalityVector(trait_values)

        with pytest.raises(ValueError, match="Unknown trait code"):
            pv.get_trait_value("X")

    def test_to_dict(self):
        """Test converting PersonalityVector to dictionary"""
        trait_values = {
            "O": 0.7,
            "C": 0.5,
            "E": 0.8,
            "A": 0.6,
            "N": 0.3
        }

        pv = PersonalityVector(trait_values)
        result = pv.to_dict()

        assert result == trait_values

    def test_trait_codes_property(self):
        """Test that trait_codes property returns correct codes in order"""
        trait_values = {
            "O": 0.7,
            "C": 0.5,
            "E": 0.8,
            "A": 0.6,
            "N": 0.3
        }

        pv = PersonalityVector(trait_values)

        assert pv.trait_codes == ["O", "C", "E", "A", "N"]
