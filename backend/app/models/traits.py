"""
OCEAN Trait System - Phase 3A

Object-oriented personality trait framework using OCEAN (Big Five) as foundation.
Designed for extensibility - future traits can be added without changing core logic.

Architecture:
- Trait: Immutable dataclass representing a single personality dimension
- TraitRegistry: Central registry of all active traits (currently 5 OCEAN traits)
- PersonalityVector: N-dimensional vector container with mathematical operations

Mathematical Framework:
- Euclidean distance for diversity measurement
- Cosine similarity for archetype affinity (in separate module)
- NumPy arrays for efficient vector operations
"""

from dataclasses import dataclass
from typing import List, Dict
import numpy as np


@dataclass(frozen=True)
class Trait:
    """
    Immutable representation of a personality trait dimension.

    Attributes:
        code: Single-letter code (e.g., "O", "C", "E", "A", "N")
        name: Full trait name (e.g., "Openness")
        description: Detailed description of what this trait measures
        low_label: Label for low values (e.g., "Conventional")
        high_label: Label for high values (e.g., "Creative")
        category: Category of trait ("psychological", "social", "economic")

    Example:
        >>> openness = Trait(
        ...     code="O",
        ...     name="Openness",
        ...     description="Openness to experience",
        ...     low_label="Conventional",
        ...     high_label="Creative",
        ...     category="psychological"
        ... )
    """
    code: str
    name: str
    description: str
    low_label: str
    high_label: str
    category: str


class TraitRegistry:
    """
    Central registry of all personality traits.

    Phase 3: Contains 5 OCEAN traits (psychological)
    Future phases can add traits by uncommenting and running migration

    Design Pattern: Static registry with class-level constants
    - Traits are immutable (frozen dataclass)
    - get_active_traits() returns only uncommented traits
    - Adding new traits requires zero changes to PersonalityVector or math logic
    """

    # ========================================================================
    # OCEAN Traits (Big Five) - Phase 3 Active Traits
    # ========================================================================

    OPENNESS = Trait(
        code="O",
        name="Openness",
        description="Openness to experience, imagination, and new ideas",
        low_label="Conventional",
        high_label="Creative",
        category="psychological"
    )

    CONSCIENTIOUSNESS = Trait(
        code="C",
        name="Conscientiousness",
        description="Organization, dependability, and self-discipline",
        low_label="Spontaneous",
        high_label="Disciplined",
        category="psychological"
    )

    EXTRAVERSION = Trait(
        code="E",
        name="Extraversion",
        description="Sociability, assertiveness, and energy level",
        low_label="Reserved",
        high_label="Outgoing",
        category="psychological"
    )

    AGREEABLENESS = Trait(
        code="A",
        name="Agreeableness",
        description="Compassion, cooperation, and trust in others",
        low_label="Skeptical",
        high_label="Trusting",
        category="psychological"
    )

    NEUROTICISM = Trait(
        code="N",
        name="Neuroticism",
        description="Emotional stability and tendency toward negative emotions",
        low_label="Stable",
        high_label="Anxious",
        category="psychological"
    )

    # ========================================================================
    # Future Extensible Traits (Phase 4+) - Currently Inactive
    # ========================================================================
    # Uncomment these in future phases and run database migration

    # RELIGIOSITY = Trait(
    #     code="R",
    #     name="Religiosity",
    #     description="Religious belief, spirituality, and faith",
    #     low_label="Secular",
    #     high_label="Devout",
    #     category="social"
    # )

    # SOCIOECONOMIC = Trait(
    #     code="Econ",
    #     name="Socioeconomic Status",
    #     description="Economic resources and social class",
    #     low_label="Working Class",
    #     high_label="Affluent",
    #     category="economic"
    # )

    @classmethod
    def get_active_traits(cls) -> List[Trait]:
        """
        Returns list of currently active traits in order.

        Phase 3: Returns 5 OCEAN traits in O-C-E-A-N order
        Future: Will include additional traits as they're uncommented

        Returns:
            List of Trait objects in canonical order

        Example:
            >>> traits = TraitRegistry.get_active_traits()
            >>> len(traits)
            5
            >>> [t.code for t in traits]
            ['O', 'C', 'E', 'A', 'N']
        """
        return [
            cls.OPENNESS,
            cls.CONSCIENTIOUSNESS,
            cls.EXTRAVERSION,
            cls.AGREEABLENESS,
            cls.NEUROTICISM,
            # Add future traits here when activated
        ]


class PersonalityVector:
    """
    N-dimensional personality vector with mathematical operations.

    Represents a persona's position in N-dimensional trait space.
    Currently N=5 (OCEAN), but architecture supports arbitrary N.

    Attributes:
        traits: List of active Trait objects
        vector: NumPy array of trait values [0.0, 1.0]

    Mathematical Operations:
        - Euclidean distance: Measures diversity between personas
        - Vector normalization: For cosine similarity (in AffinityCalculator)

    Example:
        >>> pv = PersonalityVector({
        ...     "O": 0.7,
        ...     "C": 0.5,
        ...     "E": 0.8,
        ...     "A": 0.6,
        ...     "N": 0.3
        ... })
        >>> pv.vector
        array([0.7, 0.5, 0.8, 0.6, 0.3])
    """

    def __init__(self, trait_values: Dict[str, float]):
        """
        Initialize personality vector from trait values.

        Args:
            trait_values: Dictionary mapping trait codes to values
                         Example: {"O": 0.7, "C": 0.5, ...}

        Raises:
            ValueError: If any value is outside [0.0, 1.0] range
            ValueError: If required trait is missing

        Example:
            >>> pv = PersonalityVector({"O": 0.5, "C": 0.8, "E": 0.3, "A": 0.7, "N": 0.4})
        """
        self.traits = TraitRegistry.get_active_traits()
        self.trait_codes = [trait.code for trait in self.traits]

        # Validate all required traits are present
        for code in self.trait_codes:
            if code not in trait_values:
                raise ValueError(
                    f"Missing required trait: {code}. "
                    f"Required traits: {', '.join(self.trait_codes)}"
                )

        # Validate all values are in [0.0, 1.0] range
        for code, value in trait_values.items():
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"Trait {code} value {value} must be between 0.0 and 1.0"
                )

        # Create NumPy array in canonical order
        self.vector = np.array([trait_values[code] for code in self.trait_codes])

    def euclidean_distance(self, other: 'PersonalityVector') -> float:
        """
        Calculate Euclidean distance to another PersonalityVector.

        Used for diversity measurement - larger distance means more diverse personas.

        Args:
            other: Another PersonalityVector to compare against

        Returns:
            Euclidean distance (L2 norm) as float

        Example:
            >>> pv1 = PersonalityVector({"O": 0.0, "C": 0.0, "E": 0.0, "A": 0.0, "N": 0.0})
            >>> pv2 = PersonalityVector({"O": 1.0, "C": 1.0, "E": 1.0, "A": 1.0, "N": 1.0})
            >>> pv1.euclidean_distance(pv2)
            2.23606797749979  # sqrt(5)
        """
        return float(np.linalg.norm(self.vector - other.vector))

    def get_trait_value(self, trait_code: str) -> float:
        """
        Get value for a specific trait by code.

        Args:
            trait_code: Trait code (e.g., "O", "C", "E")

        Returns:
            Trait value as float [0.0, 1.0]

        Raises:
            ValueError: If trait_code is not valid

        Example:
            >>> pv = PersonalityVector({"O": 0.7, "C": 0.5, "E": 0.8, "A": 0.6, "N": 0.3})
            >>> pv.get_trait_value("O")
            0.7
        """
        if trait_code not in self.trait_codes:
            raise ValueError(
                f"Unknown trait code: {trait_code}. "
                f"Valid codes: {', '.join(self.trait_codes)}"
            )

        index = self.trait_codes.index(trait_code)
        return float(self.vector[index])

    def to_dict(self) -> Dict[str, float]:
        """
        Convert PersonalityVector to dictionary format.

        Returns:
            Dictionary mapping trait codes to values

        Example:
            >>> pv = PersonalityVector({"O": 0.7, "C": 0.5, "E": 0.8, "A": 0.6, "N": 0.3})
            >>> pv.to_dict()
            {'O': 0.7, 'C': 0.5, 'E': 0.8, 'A': 0.6, 'N': 0.3}
        """
        return {code: float(value) for code, value in zip(self.trait_codes, self.vector)}

    def __repr__(self) -> str:
        """String representation for debugging"""
        trait_str = ", ".join(f"{code}={val:.2f}" for code, val in self.to_dict().items())
        return f"PersonalityVector({trait_str})"
