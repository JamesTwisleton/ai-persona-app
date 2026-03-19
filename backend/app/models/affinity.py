"""
Archetype Affinity Calculator - Phase 3A

Calculates affinity between PersonalityVector and predefined archetypes.

Algorithm:
1. Cosine Similarity: Measure angle between persona and archetype vectors
2. Temperature Scaling: Apply softmax with temperature parameter
3. Min-Max Normalization: Scale to [0, 1] range

Mathematical Framework:
- cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)
- softmax(x, T) = exp(x / T)
- min_max_norm(x) = (x - min) / (max - min)

This preserves the legacy system's mathematics while using OCEAN as foundation.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np

from app.models.traits import PersonalityVector


@dataclass
class Archetype:
    """
    Predefined personality archetype with OCEAN vector.

    Archetypes represent "ideal" personality types against which
    personas are compared to calculate affinity scores.

    Attributes:
        code: Unique identifier (e.g., "ANALYST", "SOCIALITE")
        name: Human-readable name (e.g., "The Analyst")
        description: What this archetype represents
        ocean_vector: PersonalityVector representing archetype's OCEAN profile

    Example:
        >>> activist = Archetype(
        ...     code="ACTIVIST",
        ...     name="The Activist",
        ...     description="Passionate about social change",
        ...     ocean_vector=PersonalityVector({
        ...         "O": 0.8, "C": 0.5, "E": 0.7, "A": 0.9, "N": 0.4
        ...     })
        ... )
    """
    code: str
    name: str
    description: str
    ocean_vector: PersonalityVector


class AffinityCalculator:
    """
    Calculates affinity between PersonalityVector and archetypes.

    Uses cosine similarity + temperature-scaled softmax + min-max normalization
    to produce affinity scores in [0, 1] range.

    Attributes:
        archetypes: List of Archetype objects to compare against

    Example:
        >>> calculator = AffinityCalculator(archetypes)
        >>> persona = PersonalityVector({"O": 0.7, "C": 0.5, ...})
        >>> affinities = calculator.calculate(persona, temperature=0.3)
        >>> affinities
        {'ANALYST': 0.85, 'SOCIALITE': 0.42, 'INNOVATOR': 0.67}
    """

    def __init__(self, archetypes: List[Archetype]):
        """
        Initialize AffinityCalculator with archetypes.

        Args:
            archetypes: List of Archetype objects

        Example:
            >>> calculator = AffinityCalculator([analyst, socialite, innovator])
        """
        self.archetypes = archetypes

    def calculate(
        self,
        persona: PersonalityVector,
        temperature: float = 0.3
    ) -> Dict[str, float]:
        """
        Calculate affinity scores between persona and all archetypes.

        Algorithm:
        1. Calculate cosine similarity for each archetype
        2. Apply temperature-scaled exponential (softmax without normalization)
        3. Apply min-max normalization to scale to [0, 1]

        Args:
            persona: PersonalityVector to calculate affinities for
            temperature: Controls distribution sharpness (default 0.3)
                        Lower = more extreme scores (sharper)
                        Higher = more uniform scores (softer)

        Returns:
            Dictionary mapping archetype codes to affinity scores [0, 1]

        Example:
            >>> affinities = calculator.calculate(persona, temperature=0.3)
            >>> affinities["ANALYST"]
            0.85
        """
        # Step 1: Calculate cosine similarities
        cosine_similarities = self._calculate_cosine_similarities(persona)

        # Step 2: Apply temperature-scaled exponential
        # This is like softmax but without the normalization step
        exp_similarities = np.exp(cosine_similarities / temperature)

        # Step 3: Min-max normalization to [0, 1]
        # This ensures all scores are in [0, 1] range
        min_val = np.min(exp_similarities)
        max_val = np.max(exp_similarities)

        if max_val - min_val < 1e-10:
            # All similarities are identical - return uniform affinities
            normalized = np.ones_like(exp_similarities) * 0.5
        else:
            normalized = (exp_similarities - min_val) / (max_val - min_val)

        # Step 4: Create result dictionary
        affinities = {
            archetype.code: float(normalized[i])
            for i, archetype in enumerate(self.archetypes)
        }

        return affinities

    def _calculate_cosine_similarities(self, persona: PersonalityVector) -> np.ndarray:
        """
        Calculate cosine similarity between persona and each archetype.

        Cosine similarity measures the angle between two vectors:
        - cos(0°) = 1.0 (identical direction)
        - cos(90°) = 0.0 (perpendicular)
        - cos(180°) = -1.0 (opposite direction)

        Formula: cos(θ) = (A · B) / (||A|| * ||B||)

        Args:
            persona: PersonalityVector to compare

        Returns:
            NumPy array of cosine similarities

        Example:
            >>> similarities = calculator._calculate_cosine_similarities(persona)
            >>> similarities
            array([0.95, 0.62, 0.78])
        """
        # Get persona vector
        persona_vector = persona.vector

        # Calculate persona norm (length)
        persona_norm = np.linalg.norm(persona_vector)

        # Calculate similarities for each archetype
        similarities = []

        for archetype in self.archetypes:
            archetype_vector = archetype.ocean_vector.vector

            # Dot product (numerator)
            dot_product = np.dot(persona_vector, archetype_vector)

            # Calculate archetype norm
            archetype_norm = np.linalg.norm(archetype_vector)

            # Cosine similarity (with epsilon to avoid division by zero)
            epsilon = 1e-10
            cosine_sim = dot_product / (persona_norm * archetype_norm + epsilon)

            similarities.append(cosine_sim)

        return np.array(similarities)

    def get_top_affinities(
        self,
        affinities: Dict[str, float],
        n: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """
        Get top N archetypes by affinity score.

        Args:
            affinities: Dictionary of affinity scores from calculate()
            n: Number of top affinities to return (None = all)

        Returns:
            List of (archetype_code, affinity) tuples sorted by affinity descending

        Example:
            >>> top_3 = calculator.get_top_affinities(affinities, n=3)
            >>> top_3
            [('ANALYST', 0.85), ('INNOVATOR', 0.67), ('SOCIALITE', 0.42)]
        """
        # Sort by affinity descending
        sorted_affinities = sorted(
            affinities.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top N (or all if n is None)
        if n is None:
            return sorted_affinities
        else:
            return sorted_affinities[:n]

    def __repr__(self) -> str:
        """String representation for debugging"""
        archetype_codes = [a.code for a in self.archetypes]
        return f"AffinityCalculator(archetypes={archetype_codes})"
