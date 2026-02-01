"""
Archetype Definitions - Phase 3A

Predefined personality archetypes using OCEAN (Big Five) model.

Each archetype represents a distinct personality type with carefully
calibrated OCEAN scores based on psychological research.

Archetypes serve as reference points for:
- Calculating persona affinities
- Guiding Claude's personality inference from backstories
- Ensuring diverse focus group composition

Design Principles:
- Each archetype occupies distinct region in 5D OCEAN space
- OCEAN scores based on empirical personality research
- Archetypes span full spectrum of human personality
"""

from app.models.traits import PersonalityVector
from app.models.affinity import Archetype


# ============================================================================
# Core Archetypes - Phase 3
# ============================================================================

THE_ANALYST = Archetype(
    code="ANALYST",
    name="The Analyst",
    description=(
        "Logical, detail-oriented, and methodical. Values data over intuition. "
        "Prefers structure and evidence-based decision making. "
        "Introverted and somewhat skeptical of others."
    ),
    ocean_vector=PersonalityVector({
        "O": 0.65,  # Moderately open (enjoys intellectual exploration)
        "C": 0.90,  # Highly conscientious (organized, disciplined)
        "E": 0.25,  # Introverted (reserved, prefers solitude)
        "A": 0.35,  # Skeptical (questions others, competitive)
        "N": 0.20   # Emotionally stable (calm under pressure)
    })
)

THE_SOCIALITE = Archetype(
    code="SOCIALITE",
    name="The Socialite",
    description=(
        "Outgoing, warm, and people-oriented. Thrives in social settings. "
        "Values relationships and harmony over logic. "
        "Optimistic and emotionally expressive."
    ),
    ocean_vector=PersonalityVector({
        "O": 0.60,  # Moderately open (curious about people/culture)
        "C": 0.40,  # Less conscientious (spontaneous, flexible)
        "E": 0.90,  # Highly extraverted (energized by social interaction)
        "A": 0.85,  # Very agreeable (trusting, cooperative)
        "N": 0.30   # Stable (generally positive emotions)
    })
)

THE_INNOVATOR = Archetype(
    code="INNOVATOR",
    name="The Innovator",
    description=(
        "Creative, visionary, and unconventional. Challenges status quo. "
        "Values imagination and new possibilities over tradition. "
        "Independent thinker with high tolerance for ambiguity."
    ),
    ocean_vector=PersonalityVector({
        "O": 0.95,  # Extremely open (imaginative, curious)
        "C": 0.45,  # Moderate conscientiousness (flexible, adaptive)
        "E": 0.60,  # Moderately extraverted (shares ideas enthusiastically)
        "A": 0.50,  # Balanced agreeableness (cooperative but independent)
        "N": 0.40   # Moderate stability (comfortable with uncertainty)
    })
)

THE_ACTIVIST = Archetype(
    code="ACTIVIST",
    name="The Activist",
    description=(
        "Passionate, principled, and driven by values. "
        "Fights for social justice and positive change. "
        "Emotionally engaged with strong moral convictions."
    ),
    ocean_vector=PersonalityVector({
        "O": 0.80,  # Very open (embraces diversity, new ideas)
        "C": 0.55,  # Moderate conscientiousness (goal-oriented but flexible)
        "E": 0.70,  # Extraverted (vocal, rallies others)
        "A": 0.85,  # Very agreeable (compassionate, altruistic)
        "N": 0.55   # Moderate neuroticism (emotionally engaged, passionate)
    })
)

THE_PRAGMATIST = Archetype(
    code="PRAGMATIST",
    name="The Pragmatist",
    description=(
        "Practical, realistic, and results-focused. "
        "Values what works over ideology or theory. "
        "Balanced, adaptable, and grounded in reality."
    ),
    ocean_vector=PersonalityVector({
        "O": 0.50,  # Balanced openness (open but selective)
        "C": 0.70,  # Conscientious (organized, reliable)
        "E": 0.55,  # Ambivert (comfortable alone or with others)
        "A": 0.60,  # Moderately agreeable (cooperative but firm)
        "N": 0.25   # Stable (even-keeled, unflappable)
    })
)

THE_TRADITIONALIST = Archetype(
    code="TRADITIONALIST",
    name="The Traditionalist",
    description=(
        "Values heritage, stability, and established norms. "
        "Respects authority and proven methods. "
        "Conscientious and duty-oriented with strong moral code."
    ),
    ocean_vector=PersonalityVector({
        "O": 0.25,  # Low openness (conventional, prefers familiar)
        "C": 0.85,  # Highly conscientious (disciplined, dutiful)
        "E": 0.45,  # Slightly introverted (reserved, formal)
        "A": 0.70,  # Agreeable (respects authority, cooperative)
        "N": 0.35   # Stable (prefers predictability)
    })
)

THE_SKEPTIC = Archetype(
    code="SKEPTIC",
    name="The Skeptic",
    description=(
        "Questioning, analytical, and cautious. "
        "Demands evidence and challenges assumptions. "
        "Independent thinker who resists groupthink."
    ),
    ocean_vector=PersonalityVector({
        "O": 0.70,  # Open to ideas (intellectually curious)
        "C": 0.65,  # Conscientious (thorough, deliberate)
        "E": 0.40,  # Introverted (reserved, observant)
        "A": 0.30,  # Low agreeableness (challenging, competitive)
        "N": 0.45   # Moderate neuroticism (cautious, vigilant)
    })
)

THE_OPTIMIST = Archetype(
    code="OPTIMIST",
    name="The Optimist",
    description=(
        "Positive, hopeful, and enthusiastic. "
        "Sees opportunities where others see obstacles. "
        "Emotionally resilient and uplifting to others."
    ),
    ocean_vector=PersonalityVector({
        "O": 0.75,  # Very open (curious, embraces new experiences)
        "C": 0.60,  # Moderately conscientious (goal-oriented but flexible)
        "E": 0.80,  # Highly extraverted (energetic, enthusiastic)
        "A": 0.80,  # Very agreeable (friendly, trusting)
        "N": 0.15   # Very stable (positive emotions, resilient)
    })
)

# ============================================================================
# Archetype Registry
# ============================================================================

ALL_ARCHETYPES = [
    THE_ANALYST,
    THE_SOCIALITE,
    THE_INNOVATOR,
    THE_ACTIVIST,
    THE_PRAGMATIST,
    THE_TRADITIONALIST,
    THE_SKEPTIC,
    THE_OPTIMIST,
]

# Create lookup dictionary for easy access
ARCHETYPES_BY_CODE = {
    archetype.code: archetype
    for archetype in ALL_ARCHETYPES
}


def get_archetype_by_code(code: str) -> Archetype:
    """
    Get archetype by code.

    Args:
        code: Archetype code (e.g., "ANALYST", "SOCIALITE")

    Returns:
        Archetype object

    Raises:
        KeyError: If code not found

    Example:
        >>> analyst = get_archetype_by_code("ANALYST")
        >>> analyst.name
        'The Analyst'
    """
    return ARCHETYPES_BY_CODE[code]


def get_all_archetypes() -> list[Archetype]:
    """
    Get all available archetypes.

    Returns:
        List of all Archetype objects

    Example:
        >>> archetypes = get_all_archetypes()
        >>> len(archetypes)
        8
    """
    return ALL_ARCHETYPES.copy()


# ============================================================================
# Archetype Diversity Analysis
# ============================================================================

def calculate_archetype_diversity() -> dict:
    """
    Calculate diversity metrics for archetype set.

    Measures how well-distributed archetypes are in OCEAN space.
    Used for quality assurance - archetypes should be diverse.

    Returns:
        Dictionary with diversity statistics

    Example:
        >>> diversity = calculate_archetype_diversity()
        >>> diversity['mean_pairwise_distance']
        1.23
    """
    from app.models.affinity import AffinityCalculator
    import numpy as np

    # Calculate pairwise Euclidean distances
    distances = []

    for i, archetype_a in enumerate(ALL_ARCHETYPES):
        for j, archetype_b in enumerate(ALL_ARCHETYPES):
            if i < j:  # Only upper triangle (avoid duplicates)
                distance = archetype_a.ocean_vector.euclidean_distance(
                    archetype_b.ocean_vector
                )
                distances.append(distance)

    return {
        "mean_pairwise_distance": float(np.mean(distances)),
        "min_pairwise_distance": float(np.min(distances)),
        "max_pairwise_distance": float(np.max(distances)),
        "std_pairwise_distance": float(np.std(distances)),
        "num_archetypes": len(ALL_ARCHETYPES),
    }
