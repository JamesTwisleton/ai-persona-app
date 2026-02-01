"""
Unit tests for AffinityCalculator (Phase 3A - TDD Cycle 2)

Tests the archetype affinity calculation system:
- Cosine similarity between PersonalityVector and archetypes
- Temperature-scaled softmax
- Min-max normalization to [0, 1]
"""

import pytest
import numpy as np
from app.models.traits import PersonalityVector
from app.models.affinity import AffinityCalculator, Archetype


class TestArchetype:
    """Test the Archetype dataclass"""

    def test_archetype_creation(self):
        """Test creating a valid Archetype"""
        archetype = Archetype(
            code="ACTIVIST",
            name="The Activist",
            description="Passionate about social change",
            ocean_vector=PersonalityVector({
                "O": 0.8,
                "C": 0.5,
                "E": 0.7,
                "A": 0.9,
                "N": 0.4
            })
        )

        assert archetype.code == "ACTIVIST"
        assert archetype.name == "The Activist"
        assert isinstance(archetype.ocean_vector, PersonalityVector)


class TestAffinityCalculator:
    """Test the AffinityCalculator class"""

    @pytest.fixture
    def sample_archetypes(self):
        """Create sample archetypes for testing"""
        return [
            Archetype(
                code="ANALYST",
                name="The Analyst",
                description="Logical and detail-oriented",
                ocean_vector=PersonalityVector({
                    "O": 0.7,  # Moderately open
                    "C": 0.9,  # Highly conscientious
                    "E": 0.3,  # Introverted
                    "A": 0.4,  # Skeptical
                    "N": 0.2   # Stable
                })
            ),
            Archetype(
                code="SOCIALITE",
                name="The Socialite",
                description="Outgoing and people-oriented",
                ocean_vector=PersonalityVector({
                    "O": 0.6,  # Moderately open
                    "C": 0.4,  # Less organized
                    "E": 0.9,  # Highly extraverted
                    "A": 0.8,  # Very agreeable
                    "N": 0.3   # Stable
                })
            ),
            Archetype(
                code="INNOVATOR",
                name="The Innovator",
                description="Creative and visionary",
                ocean_vector=PersonalityVector({
                    "O": 0.95, # Extremely open
                    "C": 0.5,  # Balanced conscientiousness
                    "E": 0.6,  # Moderately extraverted
                    "A": 0.5,  # Balanced agreeableness
                    "N": 0.4   # Stable
                })
            )
        ]

    def test_affinity_calculator_creation(self, sample_archetypes):
        """Test creating AffinityCalculator with archetypes"""
        calculator = AffinityCalculator(sample_archetypes)

        assert len(calculator.archetypes) == 3
        assert calculator.archetypes[0].code == "ANALYST"

    def test_calculate_affinities_returns_dict(self, sample_archetypes):
        """Test that calculate() returns dict with all archetype codes"""
        calculator = AffinityCalculator(sample_archetypes)

        persona = PersonalityVector({
            "O": 0.8,
            "C": 0.6,
            "E": 0.5,
            "A": 0.7,
            "N": 0.3
        })

        affinities = calculator.calculate(persona)

        assert isinstance(affinities, dict)
        assert "ANALYST" in affinities
        assert "SOCIALITE" in affinities
        assert "INNOVATOR" in affinities

    def test_affinity_values_in_range(self, sample_archetypes):
        """Test that all affinity values are in [0, 1] range"""
        calculator = AffinityCalculator(sample_archetypes)

        persona = PersonalityVector({
            "O": 0.5,
            "C": 0.5,
            "E": 0.5,
            "A": 0.5,
            "N": 0.5
        })

        affinities = calculator.calculate(persona)

        for code, affinity in affinities.items():
            assert 0.0 <= affinity <= 1.0, f"{code} affinity {affinity} not in [0, 1]"

    def test_affinity_sum_not_necessarily_one(self, sample_archetypes):
        """Test that affinities don't necessarily sum to 1 (not a probability distribution)"""
        calculator = AffinityCalculator(sample_archetypes)

        persona = PersonalityVector({
            "O": 0.5,
            "C": 0.5,
            "E": 0.5,
            "A": 0.5,
            "N": 0.5
        })

        affinities = calculator.calculate(persona)
        total = sum(affinities.values())

        # After min-max normalization, sum is NOT constrained to 1
        # This is correct - we want independent affinity scores
        assert total != pytest.approx(1.0, abs=0.1)

    def test_identical_persona_has_highest_affinity(self, sample_archetypes):
        """Test that persona identical to archetype has highest affinity to that archetype"""
        calculator = AffinityCalculator(sample_archetypes)

        # Create persona identical to ANALYST archetype
        persona = PersonalityVector({
            "O": 0.7,
            "C": 0.9,
            "E": 0.3,
            "A": 0.4,
            "N": 0.2
        })

        affinities = calculator.calculate(persona)

        # ANALYST should have highest affinity
        assert affinities["ANALYST"] > affinities["SOCIALITE"]
        assert affinities["ANALYST"] > affinities["INNOVATOR"]

    def test_opposite_persona_has_lower_affinity(self, sample_archetypes):
        """Test that persona opposite to archetype has lower affinity"""
        calculator = AffinityCalculator(sample_archetypes)

        # Create persona opposite to SOCIALITE (introverted, disagreeable)
        persona = PersonalityVector({
            "O": 0.4,  # Opposite of 0.6
            "C": 0.6,  # Opposite of 0.4
            "E": 0.1,  # Opposite of 0.9 (VERY opposite)
            "A": 0.2,  # Opposite of 0.8 (VERY opposite)
            "N": 0.7   # Opposite of 0.3
        })

        affinities = calculator.calculate(persona)

        # SOCIALITE should have lowest affinity
        assert affinities["SOCIALITE"] < affinities["ANALYST"]
        assert affinities["SOCIALITE"] < affinities["INNOVATOR"]

    def test_temperature_affects_distribution(self, sample_archetypes):
        """Test that temperature parameter affects affinity distribution"""
        calculator = AffinityCalculator(sample_archetypes)

        persona = PersonalityVector({
            "O": 0.8,
            "C": 0.6,
            "E": 0.5,
            "A": 0.7,
            "N": 0.3
        })

        # Low temperature (0.1) = more extreme, sharper distribution
        affinities_low_temp = calculator.calculate(persona, temperature=0.1)

        # High temperature (1.0) = more uniform, softer distribution
        affinities_high_temp = calculator.calculate(persona, temperature=1.0)

        # Calculate variance (spread) of affinities
        variance_low = np.var(list(affinities_low_temp.values()))
        variance_high = np.var(list(affinities_high_temp.values()))

        # Lower temperature should have higher variance (more extreme values)
        assert variance_low > variance_high

    def test_default_temperature(self, sample_archetypes):
        """Test that default temperature is 0.3"""
        calculator = AffinityCalculator(sample_archetypes)

        persona = PersonalityVector({
            "O": 0.5,
            "C": 0.5,
            "E": 0.5,
            "A": 0.5,
            "N": 0.5
        })

        # Should work without temperature parameter
        affinities = calculator.calculate(persona)
        assert len(affinities) == 3

    def test_cosine_similarity_calculation(self, sample_archetypes):
        """Test cosine similarity is calculated correctly"""
        calculator = AffinityCalculator(sample_archetypes)

        # Create persona with known cosine similarity
        # If persona = archetype, cosine similarity = 1.0
        analyst_vector = {
            "O": 0.7,
            "C": 0.9,
            "E": 0.3,
            "A": 0.4,
            "N": 0.2
        }

        persona = PersonalityVector(analyst_vector)

        # Calculate expected cosine similarity manually
        # For identical vectors: cos(θ) = 1.0
        # After temperature softmax and normalization, should have high affinity
        affinities = calculator.calculate(persona, temperature=0.3)

        # ANALYST should have very high affinity (close to 1.0 after normalization)
        assert affinities["ANALYST"] > 0.7

    def test_zero_vector_handling(self, sample_archetypes):
        """Test that calculator handles near-zero vectors gracefully"""
        calculator = AffinityCalculator(sample_archetypes)

        # Create persona with very small values (but not exactly zero)
        persona = PersonalityVector({
            "O": 0.01,
            "C": 0.01,
            "E": 0.01,
            "A": 0.01,
            "N": 0.01
        })

        # Should not crash and should return valid affinities
        affinities = calculator.calculate(persona)

        assert len(affinities) == 3
        for affinity in affinities.values():
            assert 0.0 <= affinity <= 1.0

    def test_affinity_deterministic(self, sample_archetypes):
        """Test that affinity calculation is deterministic"""
        calculator = AffinityCalculator(sample_archetypes)

        persona = PersonalityVector({
            "O": 0.6,
            "C": 0.7,
            "E": 0.4,
            "A": 0.8,
            "N": 0.5
        })

        affinities_1 = calculator.calculate(persona)
        affinities_2 = calculator.calculate(persona)

        # Should get identical results
        for code in affinities_1.keys():
            assert affinities_1[code] == pytest.approx(affinities_2[code])

    def test_get_top_affinities(self, sample_archetypes):
        """Test getting top N archetypes by affinity"""
        calculator = AffinityCalculator(sample_archetypes)

        persona = PersonalityVector({
            "O": 0.95,  # Very high openness - should match INNOVATOR
            "C": 0.5,
            "E": 0.6,
            "A": 0.5,
            "N": 0.4
        })

        affinities = calculator.calculate(persona)
        top_2 = calculator.get_top_affinities(affinities, n=2)

        # Should return list of (code, affinity) tuples
        assert len(top_2) == 2
        assert isinstance(top_2[0], tuple)
        assert isinstance(top_2[0][0], str)
        assert isinstance(top_2[0][1], float)

        # First should have higher affinity than second
        assert top_2[0][1] >= top_2[1][1]

    def test_get_top_affinities_all(self, sample_archetypes):
        """Test getting all affinities sorted"""
        calculator = AffinityCalculator(sample_archetypes)

        persona = PersonalityVector({
            "O": 0.5,
            "C": 0.5,
            "E": 0.5,
            "A": 0.5,
            "N": 0.5
        })

        affinities = calculator.calculate(persona)
        all_sorted = calculator.get_top_affinities(affinities, n=None)

        # Should return all 3 in descending order
        assert len(all_sorted) == 3
        assert all_sorted[0][1] >= all_sorted[1][1] >= all_sorted[2][1]
