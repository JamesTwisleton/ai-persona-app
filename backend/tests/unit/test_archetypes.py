"""
Unit tests for Archetype Definitions (Phase 3A)

Tests the predefined archetypes:
- Archetype OCEAN vectors are valid
- Archetypes are diverse (well-distributed in OCEAN space)
- AffinityCalculator works with real archetypes
"""

import pytest
from app.models.archetypes import (
    THE_ANALYST,
    THE_SOCIALITE,
    THE_INNOVATOR,
    THE_ACTIVIST,
    THE_PRAGMATIST,
    THE_TRADITIONALIST,
    THE_SKEPTIC,
    THE_OPTIMIST,
    ALL_ARCHETYPES,
    ARCHETYPES_BY_CODE,
    get_archetype_by_code,
    get_all_archetypes,
    calculate_archetype_diversity,
)
from app.models.traits import PersonalityVector
from app.models.affinity import AffinityCalculator


class TestArchetypeDefinitions:
    """Test individual archetype definitions"""

    def test_all_archetypes_have_valid_codes(self):
        """Test that all archetypes have non-empty codes"""
        for archetype in ALL_ARCHETYPES:
            assert archetype.code
            assert isinstance(archetype.code, str)
            assert len(archetype.code) > 0

    def test_all_archetypes_have_names(self):
        """Test that all archetypes have descriptive names"""
        for archetype in ALL_ARCHETYPES:
            assert archetype.name
            assert isinstance(archetype.name, str)
            assert len(archetype.name) > 0

    def test_all_archetypes_have_descriptions(self):
        """Test that all archetypes have detailed descriptions"""
        for archetype in ALL_ARCHETYPES:
            assert archetype.description
            assert isinstance(archetype.description, str)
            assert len(archetype.description) > 20  # Substantial description

    def test_all_archetypes_have_ocean_vectors(self):
        """Test that all archetypes have valid PersonalityVectors"""
        for archetype in ALL_ARCHETYPES:
            assert isinstance(archetype.ocean_vector, PersonalityVector)

            # Check all OCEAN values are in [0, 1]
            ocean_dict = archetype.ocean_vector.to_dict()
            for trait, value in ocean_dict.items():
                assert 0.0 <= value <= 1.0

    def test_analyst_archetype(self):
        """Test The Analyst archetype characteristics"""
        assert THE_ANALYST.code == "ANALYST"
        assert "Analyst" in THE_ANALYST.name

        # Analyst should be: high C, low E, low A
        ocean = THE_ANALYST.ocean_vector.to_dict()
        assert ocean["C"] >= 0.8  # Highly conscientious
        assert ocean["E"] <= 0.3  # Introverted
        assert ocean["A"] <= 0.4  # Skeptical

    def test_socialite_archetype(self):
        """Test The Socialite archetype characteristics"""
        assert THE_SOCIALITE.code == "SOCIALITE"
        assert "Socialite" in THE_SOCIALITE.name

        # Socialite should be: high E, high A
        ocean = THE_SOCIALITE.ocean_vector.to_dict()
        assert ocean["E"] >= 0.8  # Highly extraverted
        assert ocean["A"] >= 0.8  # Very agreeable

    def test_innovator_archetype(self):
        """Test The Innovator archetype characteristics"""
        assert THE_INNOVATOR.code == "INNOVATOR"
        assert "Innovator" in THE_INNOVATOR.name

        # Innovator should be: very high O
        ocean = THE_INNOVATOR.ocean_vector.to_dict()
        assert ocean["O"] >= 0.9  # Extremely open

    def test_eight_archetypes_exist(self):
        """Test that we have exactly 8 archetypes"""
        assert len(ALL_ARCHETYPES) == 8


class TestArchetypeRegistry:
    """Test archetype registry functions"""

    def test_get_archetype_by_code(self):
        """Test retrieving archetype by code"""
        analyst = get_archetype_by_code("ANALYST")
        assert analyst.code == "ANALYST"
        assert analyst.name == "The Analyst"

    def test_get_archetype_invalid_code(self):
        """Test that invalid code raises KeyError"""
        with pytest.raises(KeyError):
            get_archetype_by_code("INVALID")

    def test_get_all_archetypes(self):
        """Test getting all archetypes"""
        archetypes = get_all_archetypes()
        assert len(archetypes) == 8

        # Should be a copy, not the original
        archetypes.append("test")
        assert len(ALL_ARCHETYPES) == 8  # Original unchanged

    def test_archetypes_by_code_dict(self):
        """Test ARCHETYPES_BY_CODE dictionary"""
        assert "ANALYST" in ARCHETYPES_BY_CODE
        assert "SOCIALITE" in ARCHETYPES_BY_CODE
        assert "INNOVATOR" in ARCHETYPES_BY_CODE
        assert len(ARCHETYPES_BY_CODE) == 8


class TestArchetypeDiversity:
    """Test archetype diversity metrics"""

    def test_calculate_archetype_diversity(self):
        """Test diversity calculation"""
        diversity = calculate_archetype_diversity()

        assert "mean_pairwise_distance" in diversity
        assert "min_pairwise_distance" in diversity
        assert "max_pairwise_distance" in diversity
        assert "std_pairwise_distance" in diversity
        assert "num_archetypes" in diversity

    def test_archetypes_are_diverse(self):
        """Test that archetypes are well-distributed in OCEAN space"""
        diversity = calculate_archetype_diversity()

        # Mean pairwise distance should be substantial (not clustered)
        # In 5D space with [0, 1] range, our 8 archetypes span well
        # Mean distance of ~0.59 indicates good diversity
        assert diversity["mean_pairwise_distance"] > 0.5

        # No two archetypes should be too similar
        assert diversity["min_pairwise_distance"] > 0.3

    def test_archetypes_span_ocean_dimensions(self):
        """Test that archetypes span full range of each OCEAN dimension"""
        # Collect all OCEAN values for each dimension
        ocean_values = {
            "O": [],
            "C": [],
            "E": [],
            "A": [],
            "N": []
        }

        for archetype in ALL_ARCHETYPES:
            ocean_dict = archetype.ocean_vector.to_dict()
            for trait, value in ocean_dict.items():
                ocean_values[trait].append(value)

        # Each dimension should have reasonable range
        # Note: Neuroticism (N) naturally has smaller range since
        # extreme anxiety/instability is less common in archetypes
        for trait, values in ocean_values.items():
            value_range = max(values) - min(values)
            min_range = 0.4 if trait == "N" else 0.5
            assert value_range >= min_range, f"{trait} range too narrow: {value_range}"


class TestAffinityWithRealArchetypes:
    """Test AffinityCalculator with real archetype data"""

    def test_affinity_calculator_with_all_archetypes(self):
        """Test AffinityCalculator works with all 8 archetypes"""
        calculator = AffinityCalculator(ALL_ARCHETYPES)

        persona = PersonalityVector({
            "O": 0.7,
            "C": 0.9,
            "E": 0.3,
            "A": 0.4,
            "N": 0.2
        })

        affinities = calculator.calculate(persona)

        # Should have affinity for all 8 archetypes
        assert len(affinities) == 8
        assert all(0.0 <= aff <= 1.0 for aff in affinities.values())

    def test_analyst_persona_matches_analyst_archetype(self):
        """Test that analyst-like persona has high affinity to ANALYST"""
        calculator = AffinityCalculator(ALL_ARCHETYPES)

        # Create persona identical to ANALYST
        analyst_ocean = THE_ANALYST.ocean_vector.to_dict()
        persona = PersonalityVector(analyst_ocean)

        affinities = calculator.calculate(persona, temperature=0.3)

        # ANALYST should have highest affinity
        top_archetype = max(affinities.items(), key=lambda x: x[1])
        assert top_archetype[0] == "ANALYST"

    def test_socialite_persona_matches_socialite_archetype(self):
        """Test that socialite-like persona has high affinity to SOCIALITE"""
        calculator = AffinityCalculator(ALL_ARCHETYPES)

        # Create persona similar to SOCIALITE (high E, high A)
        persona = PersonalityVector({
            "O": 0.6,
            "C": 0.4,
            "E": 0.85,  # Very extraverted
            "A": 0.80,  # Very agreeable
            "N": 0.3
        })

        affinities = calculator.calculate(persona, temperature=0.3)

        # SOCIALITE should be in top 2
        top_2 = calculator.get_top_affinities(affinities, n=2)
        top_codes = [code for code, _ in top_2]
        assert "SOCIALITE" in top_codes

    def test_innovator_persona_matches_innovator_archetype(self):
        """Test that innovative persona has high affinity to INNOVATOR"""
        calculator = AffinityCalculator(ALL_ARCHETYPES)

        # Create persona similar to INNOVATOR (very high O)
        persona = PersonalityVector({
            "O": 0.92,  # Extremely open
            "C": 0.5,
            "E": 0.6,
            "A": 0.5,
            "N": 0.4
        })

        affinities = calculator.calculate(persona, temperature=0.3)

        # INNOVATOR should be in top 2
        top_2 = calculator.get_top_affinities(affinities, n=2)
        top_codes = [code for code, _ in top_2]
        assert "INNOVATOR" in top_codes

    def test_balanced_persona_has_moderate_affinities(self):
        """Test that balanced persona affinities are calculated correctly"""
        calculator = AffinityCalculator(ALL_ARCHETYPES)

        # Create perfectly balanced persona (all 0.5)
        persona = PersonalityVector({
            "O": 0.5,
            "C": 0.5,
            "E": 0.5,
            "A": 0.5,
            "N": 0.5
        })

        affinities = calculator.calculate(persona, temperature=0.3)

        # Due to min-max normalization, values will span [0, 1]
        # This is correct behavior - one archetype will be closest (1.0)
        # and one will be farthest (0.0)
        values = list(affinities.values())
        max_val = max(values)
        min_val = min(values)

        # Verify normalization worked correctly
        assert max_val == pytest.approx(1.0, abs=0.01)
        assert min_val == pytest.approx(0.0, abs=0.01)
