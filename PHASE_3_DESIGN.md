# Phase 3: Extensible N-Dimensional Personality System (OCEAN Foundation)

## Executive Summary

Phase 3 implements a **fully extensible N-dimensional personality vector system** using **OCEAN as the foundational 5 dimensions**, with object-oriented architecture enabling seamless expansion (religiosity, socioeconomics, political orientation, etc.).

**Core Innovation**: OCEAN (5D) serves as the "unit of measurement" in an N-dimensional Euclidean vector space. Adding new dimensions requires zero changes to mathematical algorithms—only trait definitions.

**Key Principles**:
- Personality = N-dimensional vector in Euclidean space
- OCEAN (5D) is the **base implementation** (not derived)
- Object-oriented `Trait` system for dimension extensibility
- All math (Euclidean distance, cosine similarity, archetype affinities) works for **any N**
- Legacy 6D system **completely removed**

---

## 1. Personality Model: Object-Oriented N-Dimensional Architecture

### 1.1 The Trait System (OOP Foundation)

**Core Classes**:

```python
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

@dataclass
class Trait:
    """
    Represents a single personality dimension.

    This is the unit of extensibility—adding a new dimension
    means adding a new Trait definition.
    """
    code: str              # "O", "C", "E", "A", "N", "R", "Econ"
    name: str              # "Openness", "Religiosity"
    description: str       # Full description
    low_label: str         # Label at 0.0 (e.g., "Conventional")
    high_label: str        # Label at 1.0 (e.g., "Curious")
    category: str          # "psychological", "social", "economic", "political"

    def __post_init__(self):
        """Validate trait definition"""
        assert 0 < len(self.code) <= 10, "Code must be 1-10 characters"
        assert self.code.isalnum(), "Code must be alphanumeric"


class TraitRegistry:
    """
    Central registry of all personality dimensions.

    To add a new dimension:
    1. Add a Trait definition here
    2. Update database migration (add column)
    3. All math automatically includes it
    """

    # OCEAN: Base 5 dimensions (always present)
    OPENNESS = Trait(
        code="O",
        name="Openness",
        description="Openness to experience, creativity, intellectual curiosity",
        low_label="Conventional, Practical",
        high_label="Creative, Curious",
        category="psychological"
    )

    CONSCIENTIOUSNESS = Trait(
        code="C",
        name="Conscientiousness",
        description="Organization, discipline, dependability",
        low_label="Spontaneous, Careless",
        high_label="Organized, Disciplined",
        category="psychological"
    )

    EXTRAVERSION = Trait(
        code="E",
        name="Extraversion",
        description="Sociability, assertiveness, energy",
        low_label="Introverted, Reserved",
        high_label="Outgoing, Energetic",
        category="psychological"
    )

    AGREEABLENESS = Trait(
        code="A",
        name="Agreeableness",
        description="Compassion, cooperation, trust",
        low_label="Competitive, Skeptical",
        high_label="Cooperative, Compassionate",
        category="psychological"
    )

    NEUROTICISM = Trait(
        code="N",
        name="Neuroticism",
        description="Emotional stability vs. anxiety",
        low_label="Stable, Calm",
        high_label="Anxious, Moody",
        category="psychological"
    )

    # ============================================================================
    # EXTENSIBLE DIMENSIONS (Phase 4+)
    # Uncomment and add database columns to activate
    # ============================================================================

    # RELIGIOSITY = Trait(
    #     code="R",
    #     name="Religiosity",
    #     description="Spiritual/religious orientation",
    #     low_label="Secular, Atheistic",
    #     high_label="Devout, Religious",
    #     category="social"
    # )

    # ECONOMIC_ORIENTATION = Trait(
    #     code="Econ",
    #     name="Economic Orientation",
    #     description="Economic ideology (left-right spectrum)",
    #     low_label="Socialist, State Control",
    #     high_label="Capitalist, Free Market",
    #     category="economic"
    # )

    # POLITICAL_AUTHORITY = Trait(
    #     code="Auth",
    #     name="Political Authority",
    #     description="View on government authority",
    #     low_label="Authoritarian",
    #     high_label="Libertarian",
    #     category="political"
    # )

    # CULTURAL_PROGRESSIVISM = Trait(
    #     code="Prog",
    #     name="Cultural Progressivism",
    #     description="Stance on social change and tradition",
    #     low_label="Traditionalist",
    #     high_label="Progressive",
    #     category="social"
    # )

    @classmethod
    def get_active_traits(cls) -> List[Trait]:
        """
        Returns all active traits (only OCEAN for Phase 3).

        In Phase 4+, uncomment additional traits above and they'll
        automatically be included.
        """
        return [
            cls.OPENNESS,
            cls.CONSCIENTIOUSNESS,
            cls.EXTRAVERSION,
            cls.AGREEABLENESS,
            cls.NEUROTICISM,
        ]

    @classmethod
    def get_trait_by_code(cls, code: str) -> Trait:
        """Lookup trait by code"""
        for trait in cls.get_active_traits():
            if trait.code == code:
                return trait
        raise ValueError(f"Unknown trait code: {code}")

    @classmethod
    def get_dimension_count(cls) -> int:
        """Returns N (number of active dimensions)"""
        return len(cls.get_active_traits())
```

**Usage Example**:
```python
# Get current dimensionality
N = TraitRegistry.get_dimension_count()  # 5 for Phase 3

# Add religiosity in Phase 4:
# 1. Uncomment RELIGIOSITY in TraitRegistry
# 2. Run migration: ALTER TABLE personas ADD COLUMN religiosity FLOAT
# 3. Done! All math automatically uses N=6
```

---

### 1.2 PersonalityVector: N-Dimensional Container

```python
import numpy as np
from typing import Dict

class PersonalityVector:
    """
    Represents a persona's position in N-dimensional personality space.

    Automatically adapts to the number of active traits in TraitRegistry.
    """

    def __init__(self, trait_values: Dict[str, float]):
        """
        Args:
            trait_values: {"O": 0.7, "C": 0.3, "E": 0.8, "A": 0.5, "N": 0.4}

        Raises:
            ValueError: If values are out of range [0, 1]
        """
        self.traits = TraitRegistry.get_active_traits()
        self.trait_codes = [t.code for t in self.traits]

        # Validate all traits are provided
        for code in self.trait_codes:
            if code not in trait_values:
                raise ValueError(f"Missing trait value for: {code}")

            value = trait_values[code]
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"Trait {code} value {value} out of range [0, 1]")

        # Store as numpy array for math operations
        self.vector = np.array([trait_values[code] for code in self.trait_codes])
        self.trait_values = trait_values

    def euclidean_distance(self, other: 'PersonalityVector') -> float:
        """
        Calculate Euclidean distance to another personality.

        Used for diversity measurement: higher distance = more diverse

        Returns:
            Distance in range [0, sqrt(N)]
        """
        return float(np.linalg.norm(self.vector - other.vector))

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization"""
        return self.trait_values

    @classmethod
    def random(cls, seed: int = None) -> 'PersonalityVector':
        """Generate random personality vector"""
        if seed:
            np.random.seed(seed)

        trait_codes = [t.code for t in TraitRegistry.get_active_traits()]
        values = {code: float(np.random.uniform(0, 1)) for code in trait_codes}
        return cls(values)

    def __repr__(self):
        traits_str = ", ".join([f"{code}={v:.2f}" for code, v in self.trait_values.items()])
        return f"PersonalityVector({traits_str})"
```

**Example Usage**:
```python
# Barry's personality (high C, low A)
barry = PersonalityVector({
    "O": 0.2, "C": 0.9, "E": 0.3, "A": 0.1, "N": 0.7
})

# Susan's personality (balanced)
susan = PersonalityVector({
    "O": 0.5, "C": 0.6, "E": 0.5, "A": 0.7, "N": 0.4
})

# Calculate diversity
distance = barry.euclidean_distance(susan)
print(f"Distance: {distance:.3f}")  # ~0.8 (diverse enough)
```

---

### 1.3 Archetype System: Reference Points in N-Space

**Archetype Definition**:
```python
@dataclass
class Archetype:
    """
    A reference point in personality space.

    Archetypes are fixed personas that define "ideal types" for
    calculating affinities via cosine similarity.
    """
    name: str
    description: str
    personality: PersonalityVector

    def __post_init__(self):
        """Validate archetype"""
        assert len(self.name) > 0, "Archetype must have a name"


class ArchetypeRegistry:
    """
    Defines the 6 archetypes using OCEAN dimensions.

    These replace the legacy 6D archetypes but serve the same purpose:
    providing reference points for calculating persona affinities.
    """

    # Archetype 1: The Conscientious Organizer
    ORGANIZER = Archetype(
        name="The Conscientious Organizer",
        description="Highly organized, dependable, prefers structure and order",
        personality=PersonalityVector({
            "O": 0.4,  # Moderate openness
            "C": 0.95, # Very high conscientiousness
            "E": 0.5,  # Balanced extraversion
            "A": 0.7,  # Cooperative
            "N": 0.3   # Low neuroticism (stable)
        })
    )

    # Archetype 2: The Creative Explorer
    EXPLORER = Archetype(
        name="The Creative Explorer",
        description="Highly creative, curious, open to new experiences",
        personality=PersonalityVector({
            "O": 0.95, # Very high openness
            "C": 0.3,  # Lower conscientiousness (spontaneous)
            "E": 0.7,  # Outgoing
            "A": 0.6,  # Moderately agreeable
            "N": 0.5   # Balanced emotional stability
        })
    )

    # Archetype 3: The Social Connector
    CONNECTOR = Archetype(
        name="The Social Connector",
        description="Extraverted, agreeable, thrives on social interaction",
        personality=PersonalityVector({
            "O": 0.6,  # Moderately open
            "C": 0.5,  # Balanced
            "E": 0.95, # Very high extraversion
            "A": 0.9,  # Very high agreeableness
            "N": 0.4   # Stable
        })
    )

    # Archetype 4: The Analytical Skeptic
    SKEPTIC = Archetype(
        name="The Analytical Skeptic",
        description="Questioning, competitive, values logic over emotion",
        personality=PersonalityVector({
            "O": 0.7,  # Open to ideas (analytically)
            "C": 0.8,  # Disciplined thinking
            "E": 0.3,  # Introverted
            "A": 0.2,  # Low agreeableness (skeptical)
            "N": 0.5   # Balanced
        })
    )

    # Archetype 5: The Anxious Worrier
    WORRIER = Archetype(
        name="The Anxious Worrier",
        description="Emotionally sensitive, anxious, risk-averse",
        personality=PersonalityVector({
            "O": 0.4,  # Prefers familiar
            "C": 0.6,  # Somewhat organized (coping mechanism)
            "E": 0.2,  # Introverted
            "A": 0.7,  # Agreeable (avoids conflict)
            "N": 0.95  # Very high neuroticism
        })
    )

    # Archetype 6: The Balanced Realist
    REALIST = Archetype(
        name="The Balanced Realist",
        description="Even-keeled, pragmatic, avoids extremes",
        personality=PersonalityVector({
            "O": 0.5,  # Balanced
            "C": 0.5,  # Balanced
            "E": 0.5,  # Balanced
            "A": 0.5,  # Balanced
            "N": 0.5   # Balanced
        })
    )

    @classmethod
    def get_all(cls) -> List[Archetype]:
        """Returns all defined archetypes"""
        return [
            cls.ORGANIZER,
            cls.EXPLORER,
            cls.CONNECTOR,
            cls.SKEPTIC,
            cls.WORRIER,
            cls.REALIST
        ]
```

---

### 1.4 Affinity Calculator: Cosine Similarity + Temperature Scaling

```python
class AffinityCalculator:
    """
    Calculates persona's affinity to archetypes using cosine similarity
    and temperature-scaled softmax normalization.

    Preserves exact algorithm from legacy system, adapted for N dimensions.
    """

    def __init__(self, archetypes: List[Archetype]):
        """
        Args:
            archetypes: List of reference archetypes
        """
        self.archetypes = archetypes
        self.archetype_names = [arch.name for arch in archetypes]

        # Stack archetype vectors into matrix for vectorized operations
        self.archetype_matrix = np.vstack([
            arch.personality.vector for arch in archetypes
        ])

    def calculate(self, persona: PersonalityVector, temperature: float = 0.3) -> Dict[str, float]:
        """
        Calculate normalized affinities to each archetype.

        Algorithm (from legacy utils.py):
        1. Cosine similarity: cos(θ) = (A · B) / (||A|| ||B||)
        2. Temperature-scaled softmax: exp(similarity / T)
        3. Min-max normalization to [0, 1]

        Args:
            persona: Persona's personality vector
            temperature: Controls sharpness of distribution
                - 0.1 = Very sharp (strong preference)
                - 0.3 = Balanced (default, from legacy)
                - 1.0 = Smooth (all archetypes represented)

        Returns:
            {"The Conscientious Organizer": 0.82, "The Creative Explorer": 0.05, ...}
        """
        # Cosine similarity
        dot_products = self.archetype_matrix @ persona.vector
        archetype_norms = np.linalg.norm(self.archetype_matrix, axis=1)
        persona_norm = np.linalg.norm(persona.vector)

        cosine_similarities = dot_products / (archetype_norms * persona_norm + 1e-10)

        # Temperature-scaled softmax
        exp_similarities = np.exp(cosine_similarities / temperature)

        # Min-max normalization to [0, 1]
        min_val = np.min(exp_similarities)
        max_val = np.max(exp_similarities)

        if max_val > min_val:
            normalized = (exp_similarities - min_val) / (max_val - min_val)
        else:
            # All equal—uniform distribution
            normalized = np.ones_like(exp_similarities) / len(exp_similarities)

        return {
            name: round(float(score), 3)
            for name, score in zip(self.archetype_names, normalized)
        }
```

**Example Usage**:
```python
# Calculate Barry's archetype affinities
barry = PersonalityVector({"O": 0.2, "C": 0.9, "E": 0.3, "A": 0.1, "N": 0.7})

calculator = AffinityCalculator(ArchetypeRegistry.get_all())
affinities = calculator.calculate(barry, temperature=0.3)

print(affinities)
# {
#   "The Conscientious Organizer": 0.82,  # Strong match
#   "The Analytical Skeptic": 0.35,       # Moderate match
#   "The Creative Explorer": 0.05,        # Weak match
#   ...
# }
```

---

## 2. Database Schema: N-Dimensional Storage

### 2.1 Core Tables

```sql
-- Traits: Dimension definitions (populated from TraitRegistry)
CREATE TABLE traits (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,        -- "O", "C", "E", "A", "N"
    name VARCHAR(100) NOT NULL,              -- "Openness"
    description TEXT,
    low_label VARCHAR(100),                  -- "Conventional, Practical"
    high_label VARCHAR(100),                 -- "Creative, Curious"
    category VARCHAR(50),                    -- "psychological", "social", "economic"
    is_active BOOLEAN DEFAULT TRUE,          -- Enable/disable dimensions
    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed OCEAN traits
INSERT INTO traits (code, name, description, low_label, high_label, category) VALUES
('O', 'Openness', 'Openness to experience, creativity, intellectual curiosity', 'Conventional, Practical', 'Creative, Curious', 'psychological'),
('C', 'Conscientiousness', 'Organization, discipline, dependability', 'Spontaneous, Careless', 'Organized, Disciplined', 'psychological'),
('E', 'Extraversion', 'Sociability, assertiveness, energy', 'Introverted, Reserved', 'Outgoing, Energetic', 'psychological'),
('A', 'Agreeableness', 'Compassion, cooperation, trust', 'Competitive, Skeptical', 'Cooperative, Compassionate', 'psychological'),
('N', 'Neuroticism', 'Emotional stability vs. anxiety', 'Stable, Calm', 'Anxious, Moody', 'psychological');

-- Personas: User's AI personas
CREATE TABLE personas (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Demographics
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    date_of_birth DATE,
    location VARCHAR(100),
    occupation VARCHAR(100),
    background TEXT,                         -- Claude-generated backstory

    -- OCEAN Personality Traits (Phase 3)
    openness FLOAT CHECK (openness >= 0 AND openness <= 1),
    conscientiousness FLOAT CHECK (conscientiousness >= 0 AND conscientiousness <= 1),
    extraversion FLOAT CHECK (extraversion >= 0 AND extraversion <= 1),
    agreeableness FLOAT CHECK (agreeableness >= 0 AND agreeableness <= 1),
    neuroticism FLOAT CHECK (neuroticism >= 0 AND neuroticism <= 1),

    -- Future extensible traits (Phase 4+)
    -- Uncomment when TraitRegistry is expanded:
    -- religiosity FLOAT CHECK (religiosity >= 0 AND religiosity <= 1),
    -- economic_orientation FLOAT CHECK (economic_orientation >= 0 AND economic_orientation <= 1),
    -- political_authority FLOAT CHECK (political_authority >= 0 AND political_authority <= 1),
    -- cultural_progressivism FLOAT CHECK (cultural_progressivism >= 0 AND cultural_progressivism <= 1),

    -- Metadata
    profile_picture_url VARCHAR(512),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Archetypes: Reference points in personality space
CREATE TABLE archetypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,

    -- OCEAN coordinates
    openness FLOAT NOT NULL,
    conscientiousness FLOAT NOT NULL,
    extraversion FLOAT NOT NULL,
    agreeableness FLOAT NOT NULL,
    neuroticism FLOAT NOT NULL,

    -- Future extensible traits
    -- religiosity FLOAT,
    -- economic_orientation FLOAT,
    -- political_authority FLOAT,
    -- cultural_progressivism FLOAT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed 6 archetypes
INSERT INTO archetypes (name, description, openness, conscientiousness, extraversion, agreeableness, neuroticism) VALUES
('The Conscientious Organizer', 'Highly organized, dependable, prefers structure and order', 0.4, 0.95, 0.5, 0.7, 0.3),
('The Creative Explorer', 'Highly creative, curious, open to new experiences', 0.95, 0.3, 0.7, 0.6, 0.5),
('The Social Connector', 'Extraverted, agreeable, thrives on social interaction', 0.6, 0.5, 0.95, 0.9, 0.4),
('The Analytical Skeptic', 'Questioning, competitive, values logic over emotion', 0.7, 0.8, 0.3, 0.2, 0.5),
('The Anxious Worrier', 'Emotionally sensitive, anxious, risk-averse', 0.4, 0.6, 0.2, 0.7, 0.95),
('The Balanced Realist', 'Even-keeled, pragmatic, avoids extremes', 0.5, 0.5, 0.5, 0.5, 0.5);

-- Conversations: Focus group sessions
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Topic
    topic TEXT NOT NULL,                     -- e.g., "Should the UK rejoin the EU?"
    context TEXT,                            -- Optional elaboration

    -- Metadata
    status VARCHAR(20) DEFAULT 'active',     -- active, completed, archived
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversation Participants: Who's in this conversation
CREATE TABLE conversation_participants (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    persona_id INTEGER REFERENCES personas(id) ON DELETE CASCADE,

    role VARCHAR(50) DEFAULT 'participant',  -- participant, moderator
    joined_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(conversation_id, persona_id)
);

-- Messages: Individual responses in conversation
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,

    -- Source and Target (from user requirement)
    source_persona_id INTEGER REFERENCES personas(id) ON DELETE CASCADE,  -- Who sent it
    target_persona_id INTEGER REFERENCES personas(id) ON DELETE SET NULL, -- Who it's aimed at (NULL = everyone)

    -- Content
    content TEXT NOT NULL,

    -- Metadata
    turn_number INTEGER NOT NULL,            -- Chronological order (1, 2, 3...)
    toxicity FLOAT CHECK (toxicity >= 0 AND toxicity <= 1),
    sentiment VARCHAR(20),                   -- positive, negative, neutral

    -- Archetype affinities at generation time (snapshot)
    archetype_affinities JSONB,              -- {"The Conscientious Organizer": 0.82, ...}

    created_at TIMESTAMP DEFAULT NOW()
);

-- Persona States: Conversation-specific state tracking (from user requirement)
CREATE TABLE persona_states (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER REFERENCES personas(id) ON DELETE CASCADE,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,

    -- State after each turn
    turn_number INTEGER NOT NULL,

    -- Conversation memory (for multi-turn)
    conversation_summary TEXT,               -- Claude-generated summary
    emotional_state JSONB,                   -- {"anger": 0.3, "excitement": 0.7}

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(persona_id, conversation_id, turn_number)
);

-- Indexes
CREATE INDEX idx_personas_user_id ON personas(user_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_source_persona_id ON messages(source_persona_id);
CREATE INDEX idx_messages_turn_number ON messages(conversation_id, turn_number);
CREATE INDEX idx_persona_states_lookup ON persona_states(persona_id, conversation_id);
```

### 2.2 Adding New Dimensions (Phase 4 Example)

**Step 1: Uncomment trait in TraitRegistry**
```python
# In TraitRegistry:
RELIGIOSITY = Trait(
    code="R",
    name="Religiosity",
    description="Spiritual/religious orientation",
    low_label="Secular, Atheistic",
    high_label="Devout, Religious",
    category="social"
)
```

**Step 2: Database migration**
```sql
-- Add column to personas
ALTER TABLE personas ADD COLUMN religiosity FLOAT
    CHECK (religiosity >= 0 AND religiosity <= 1);

-- Add column to archetypes
ALTER TABLE archetypes ADD COLUMN religiosity FLOAT;

-- Update existing archetypes with default values
UPDATE archetypes SET religiosity = 0.5 WHERE religiosity IS NULL;

-- Add trait metadata
INSERT INTO traits (code, name, description, low_label, high_label, category)
VALUES ('R', 'Religiosity', 'Spiritual/religious orientation', 'Secular, Atheistic', 'Devout, Religious', 'social');
```

**Step 3: Done!**
All math (Euclidean distance, cosine similarity, affinities) automatically uses N=6 dimensions.

---

## 3. Diversity Algorithm: Euclidean Distance

```python
class DiversityEngine:
    """
    Generates diverse persona sets using Euclidean distance constraints.

    Ensures personas are sufficiently different to create interesting
    focus group dynamics.
    """

    def __init__(self, min_distance: float = 0.3):
        """
        Args:
            min_distance: Minimum Euclidean distance between any two personas
                - 0.3 = Moderately diverse (default)
                - 0.5 = Highly diverse
                - 0.1 = Allow similar personas
        """
        self.min_distance = min_distance

    def generate_diverse_set(self, count: int, max_attempts: int = 1000) -> List[PersonalityVector]:
        """
        Generate N diverse personalities.

        Args:
            count: Number of personas to generate
            max_attempts: Max iterations before giving up

        Returns:
            List of PersonalityVector objects

        Raises:
            ValueError: If can't generate diverse set within max_attempts
        """
        personas = []

        for attempt in range(max_attempts):
            # Generate random candidate
            candidate = PersonalityVector.random()

            # Check distance to all existing personas
            if self._is_sufficiently_diverse(candidate, personas):
                personas.append(candidate)

                if len(personas) == count:
                    return personas

        raise ValueError(
            f"Could not generate {count} diverse personas with min_distance={self.min_distance} "
            f"in {max_attempts} attempts. Try lowering min_distance."
        )

    def _is_sufficiently_diverse(self, candidate: PersonalityVector, existing: List[PersonalityVector]) -> bool:
        """Check if candidate meets minimum distance threshold"""
        if not existing:
            return True

        for persona in existing:
            distance = candidate.euclidean_distance(persona)
            if distance < self.min_distance:
                return False

        return True

    def calculate_diversity_score(self, personas: List[PersonalityVector]) -> float:
        """
        Calculate average pairwise distance (diversity metric).

        Returns:
            Average Euclidean distance across all pairs
        """
        if len(personas) < 2:
            return 0.0

        distances = []
        for i in range(len(personas)):
            for j in range(i + 1, len(personas)):
                distances.append(personas[i].euclidean_distance(personas[j]))

        return float(np.mean(distances))
```

**Example Usage**:
```python
# Generate 5 diverse personas
engine = DiversityEngine(min_distance=0.3)
personas = engine.generate_diverse_set(count=5)

# Check diversity
diversity_score = engine.calculate_diversity_score(personas)
print(f"Average distance: {diversity_score:.3f}")  # Higher = more diverse
```

---

## 4. Persona Compatibility Analysis

### 4.1 Compatibility Calculator

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np

@dataclass
class CompatibilityScore:
    """Results of persona compatibility analysis"""
    overall_score: float  # 0.0 (incompatible) to 1.0 (highly compatible)
    diversity_score: float  # Euclidean distance (higher = more diverse)
    conflict_potential: float  # 0.0 (low) to 1.0 (high)
    synergy_potential: float  # 0.0 (low) to 1.0 (high)
    trait_analysis: Dict[str, str]  # Detailed trait-by-trait analysis
    recommendation: str  # Overall assessment


class PersonaCompatibilityAnalyzer:
    """
    Analyzes compatibility between two personas using OCEAN traits.

    Considers:
    - Diversity (Euclidean distance): Too similar = boring, too different = conflict
    - Specific trait combinations: E.g., both low A = conflict potential
    - Complementary strengths: E.g., high C + low C can balance
    """

    def analyze_compatibility(
        self,
        persona_a: PersonalityVector,
        persona_b: PersonalityVector
    ) -> CompatibilityScore:
        """
        Analyze compatibility between two personas.

        Args:
            persona_a: First persona's personality vector
            persona_b: Second persona's personality vector

        Returns:
            CompatibilityScore with detailed analysis
        """
        # 1. Calculate diversity (Euclidean distance)
        diversity = persona_a.euclidean_distance(persona_b)

        # 2. Analyze trait-by-trait for conflict/synergy
        trait_analysis = {}
        conflict_indicators = 0
        synergy_indicators = 0

        traits_a = persona_a.to_dict()
        traits_b = persona_b.to_dict()

        # Openness analysis
        o_diff = abs(traits_a['O'] - traits_b['O'])
        if o_diff < 0.3:
            trait_analysis['O'] = "Similar openness levels - likely to agree on novelty vs. tradition"
            synergy_indicators += 1
        elif o_diff > 0.7:
            trait_analysis['O'] = "Very different openness - may clash on approaches to new ideas"
            conflict_indicators += 1
        else:
            trait_analysis['O'] = "Moderate difference in openness - can provide balanced perspectives"
            synergy_indicators += 0.5

        # Conscientiousness analysis
        c_diff = abs(traits_a['C'] - traits_b['C'])
        if c_diff > 0.6:
            trait_analysis['C'] = "Different organizational styles - one structured, one flexible (complementary)"
            synergy_indicators += 1
        elif traits_a['C'] > 0.7 and traits_b['C'] > 0.7:
            trait_analysis['C'] = "Both highly organized - will work well on structured tasks"
            synergy_indicators += 1
        else:
            trait_analysis['C'] = "Similar conscientiousness - compatible work styles"

        # Extraversion analysis
        e_diff = abs(traits_a['E'] - traits_b['E'])
        if e_diff > 0.6:
            trait_analysis['E'] = "Complementary energy levels - extrovert and introvert can balance each other"
            synergy_indicators += 0.5
        else:
            trait_analysis['E'] = "Similar energy levels - comfortable communication style"
            synergy_indicators += 0.5

        # Agreeableness analysis (critical for conflict)
        a_avg = (traits_a['A'] + traits_b['A']) / 2
        if traits_a['A'] < 0.3 and traits_b['A'] < 0.3:
            trait_analysis['A'] = "Both low agreeableness - HIGH CONFLICT POTENTIAL (competitive personalities)"
            conflict_indicators += 2  # Weight this heavily
        elif a_avg > 0.6:
            trait_analysis['A'] = "High agreeableness - cooperative and harmonious interaction likely"
            synergy_indicators += 1.5
        elif abs(traits_a['A'] - traits_b['A']) > 0.5:
            trait_analysis['A'] = "Mixed agreeableness - one diplomatic, one competitive (can create tension)"
            conflict_indicators += 0.5
        else:
            trait_analysis['A'] = "Moderate agreeableness - balanced give-and-take"

        # Neuroticism analysis
        if traits_a['N'] > 0.7 and traits_b['N'] > 0.7:
            trait_analysis['N'] = "Both high neuroticism - may amplify each other's anxieties"
            conflict_indicators += 0.5
        elif abs(traits_a['N'] - traits_b['N']) > 0.5:
            trait_analysis['N'] = "Different emotional stability - stable one may balance anxious one"
            synergy_indicators += 0.5
        else:
            trait_analysis['N'] = "Similar emotional patterns - compatible stress responses"

        # 3. Calculate conflict and synergy potentials
        max_conflict = 4.0  # Maximum possible conflict indicators
        max_synergy = 5.5   # Maximum possible synergy indicators

        conflict_potential = min(conflict_indicators / max_conflict, 1.0)
        synergy_potential = min(synergy_indicators / max_synergy, 1.0)

        # 4. Calculate overall compatibility score
        # Optimal diversity: 0.3 - 0.8 (sweet spot for interesting but not hostile)
        diversity_factor = 0.0
        if 0.3 <= diversity <= 0.8:
            diversity_factor = 1.0  # Ideal diversity
        elif diversity < 0.3:
            diversity_factor = diversity / 0.3  # Too similar
        else:
            diversity_factor = max(0, 1.0 - (diversity - 0.8) / 0.5)  # Too different

        # Weight factors
        overall_score = (
            diversity_factor * 0.3 +        # 30% weight on diversity
            (1 - conflict_potential) * 0.4 + # 40% weight on low conflict
            synergy_potential * 0.3          # 30% weight on synergy
        )

        # 5. Generate recommendation
        if overall_score >= 0.75:
            recommendation = "HIGHLY COMPATIBLE - Great pairing for productive discussion"
        elif overall_score >= 0.6:
            recommendation = "COMPATIBLE - Should work well together"
        elif overall_score >= 0.4:
            recommendation = "MODERATELY COMPATIBLE - May have some tension but workable"
        elif overall_score >= 0.25:
            recommendation = "LOW COMPATIBILITY - Potential for conflict, use with caution"
        else:
            recommendation = "INCOMPATIBLE - High conflict risk, consider different pairing"

        # Add specific warnings
        if conflict_potential > 0.6:
            recommendation += " ⚠️ HIGH CONFLICT RISK"
        if diversity < 0.2:
            recommendation += " ⚠️ TOO SIMILAR - May lack diverse perspectives"
        if diversity > 1.0:
            recommendation += " ⚠️ VERY DIFFERENT - May struggle to find common ground"

        return CompatibilityScore(
            overall_score=round(overall_score, 3),
            diversity_score=round(diversity, 3),
            conflict_potential=round(conflict_potential, 3),
            synergy_potential=round(synergy_potential, 3),
            trait_analysis=trait_analysis,
            recommendation=recommendation
        )

    def analyze_group_compatibility(
        self,
        personas: List[PersonalityVector]
    ) -> Dict:
        """
        Analyze compatibility across an entire group.

        Args:
            personas: List of personality vectors

        Returns:
            Group compatibility analysis with pairwise scores
        """
        if len(personas) < 2:
            raise ValueError("Need at least 2 personas for compatibility analysis")

        # Pairwise compatibility matrix
        n = len(personas)
        compatibility_matrix = []

        for i in range(n):
            for j in range(i + 1, n):
                score = self.analyze_compatibility(personas[i], personas[j])
                compatibility_matrix.append({
                    "persona_a_index": i,
                    "persona_b_index": j,
                    "compatibility": score
                })

        # Calculate group metrics
        avg_compatibility = np.mean([c["compatibility"].overall_score for c in compatibility_matrix])
        avg_diversity = np.mean([c["compatibility"].diversity_score for c in compatibility_matrix])
        max_conflict = max([c["compatibility"].conflict_potential for c in compatibility_matrix])

        # Group assessment
        if avg_compatibility >= 0.65:
            group_assessment = "WELL-BALANCED GROUP - Good mix of personalities"
        elif avg_compatibility >= 0.5:
            group_assessment = "ACCEPTABLE GROUP - Should function adequately"
        elif avg_compatibility >= 0.35:
            group_assessment = "CHALLENGING GROUP - Expect some conflicts"
        else:
            group_assessment = "HIGH-RISK GROUP - Major conflicts likely"

        if max_conflict > 0.7:
            group_assessment += " ⚠️ Contains high-conflict pairing(s)"

        return {
            "group_size": n,
            "pairwise_compatibility": compatibility_matrix,
            "average_compatibility": round(avg_compatibility, 3),
            "average_diversity": round(avg_diversity, 3),
            "max_conflict_potential": round(max_conflict, 3),
            "group_assessment": group_assessment
        }
```

### 4.2 Compatibility API Endpoint

```python
from pydantic import BaseModel
from typing import List

class CompatibilityRequest(BaseModel):
    """Request to analyze compatibility between personas"""
    persona_uuids: List[str] = Field(..., min_items=2, max_items=10)


@router.post("/personas/compatibility")
async def analyze_persona_compatibility(
    request: CompatibilityRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze compatibility between multiple personas.

    Returns pairwise compatibility scores and group assessment.

    **Example Request:**
    ```json
    {
      "persona_uuids": ["barry-uuid", "susan-uuid", "katie-uuid"]
    }
    ```

    **Example Response:**
    ```json
    {
      "group_size": 3,
      "pairwise_compatibility": [
        {
          "persona_a": "Barry Thompson",
          "persona_b": "Susan Chen",
          "compatibility": {
            "overall_score": 0.68,
            "diversity_score": 0.45,
            "conflict_potential": 0.25,
            "synergy_potential": 0.72,
            "trait_analysis": {
              "O": "Moderate difference...",
              "C": "Both highly organized...",
              ...
            },
            "recommendation": "COMPATIBLE - Should work well together"
          }
        },
        ...
      ],
      "average_compatibility": 0.62,
      "average_diversity": 0.51,
      "max_conflict_potential": 0.35,
      "group_assessment": "WELL-BALANCED GROUP - Good mix of personalities"
    }
    ```
    """
    # Fetch personas
    personas_db = db.query(Persona).filter(
        Persona.uuid.in_(request.persona_uuids),
        Persona.user_id == current_user.id
    ).all()

    if len(personas_db) != len(request.persona_uuids):
        raise HTTPException(status_code=404, detail="One or more personas not found")

    # Create PersonalityVector objects
    personality_vectors = []
    persona_names = []

    for p in personas_db:
        personality_vectors.append(PersonalityVector({
            "O": p.openness,
            "C": p.conscientiousness,
            "E": p.extraversion,
            "A": p.agreeableness,
            "N": p.neuroticism
        }))
        persona_names.append(p.name)

    # Analyze compatibility
    analyzer = PersonaCompatibilityAnalyzer()
    group_analysis = analyzer.analyze_group_compatibility(personality_vectors)

    # Format response with persona names
    formatted_pairwise = []
    for item in group_analysis["pairwise_compatibility"]:
        i = item["persona_a_index"]
        j = item["persona_b_index"]

        formatted_pairwise.append({
            "persona_a": {
                "uuid": personas_db[i].uuid,
                "name": persona_names[i]
            },
            "persona_b": {
                "uuid": personas_db[j].uuid,
                "name": persona_names[j]
            },
            "compatibility": {
                "overall_score": item["compatibility"].overall_score,
                "diversity_score": item["compatibility"].diversity_score,
                "conflict_potential": item["compatibility"].conflict_potential,
                "synergy_potential": item["compatibility"].synergy_potential,
                "trait_analysis": item["compatibility"].trait_analysis,
                "recommendation": item["compatibility"].recommendation
            }
        })

    return {
        "group_size": group_analysis["group_size"],
        "pairwise_compatibility": formatted_pairwise,
        "average_compatibility": group_analysis["average_compatibility"],
        "average_diversity": group_analysis["average_diversity"],
        "max_conflict_potential": group_analysis["max_conflict_potential"],
        "group_assessment": group_analysis["group_assessment"]
    }
```

---

## 5. Persona Generation: Backstory-Driven OCEAN Inference

### 4.1 Generation Hierarchy

**User provides** → **Claude infers** → **System calculates**

```
Demographics + Optional Backstory    →    OCEAN Traits    →    Archetype Affinities
(User input)                              (Claude-generated)   (Cosine similarity)
```

**Required Demographics**:
- Name
- Age
- Occupation
- Location (where they live)

**Optional**:
- Background (detailed personality description)
- OCEAN override (manual scores)

**Example Flow (with backstory)**:
```
User: Name: "Barry Thompson"
      Age: 42
      Occupation: "Financial Analyst"
      Location: "Manchester, UK"
      Background: "A meticulous professional who is skeptical of change
                   and prefers data over intuition."

       ↓

Claude: Analyzes demographics + backstory →
       Demographics signals:
         - Age 42: Mid-career, established patterns
         - Occupation "Financial Analyst": Analytical, detail-oriented (C+)
         - Location "Manchester, UK": Industrial city context

       Backstory signals:
         - "meticulous" → high C (0.9)
         - "skeptical of change" → low O (0.2)
         - "data over intuition" → low A (0.1)
         - "prefers data" → analytical, introverted E (0.3)

       Combined inference:
       O=0.2, C=0.9, E=0.3, A=0.1, N=0.7

       ↓

System: Calculates archetype affinities →
       "The Conscientious Organizer": 0.82
       "The Analytical Skeptic": 0.35
       ...
```

**Example Flow (demographics only)**:
```
User: Name: "Katie Williams"
      Age: 28
      Occupation: "Environmental Activist"
      Location: "Brighton, UK"
      (No backstory provided)

       ↓

Claude: Infers from demographics alone →
       Demographics signals:
         - Age 28: Younger generation, typically more open (O+)
         - Occupation "Environmental Activist":
           * High openness (O+, progressive causes)
           * High agreeableness (A+, collective welfare)
           * Moderate-high extraversion (E+, public-facing)
         - Location "Brighton, UK": Progressive coastal city (O+ context)
         - Name "Katie Williams": Common UK name, approachable

       Inferred personality:
       O=0.85, C=0.55, E=0.70, A=0.75, N=0.45

       ↓

System: Calculates archetype affinities →
       "The Creative Explorer": 0.78
       "The Social Connector": 0.65
       ...
```

### 4.2 OCEAN Inference Prompt

```python
def build_ocean_inference_prompt(persona_description: dict) -> str:
    """
    Constructs prompt for Claude to infer OCEAN traits from demographics and optional backstory.

    Args:
        persona_description: {
            "name": "Barry Thompson",
            "age": 42,
            "occupation": "Financial Analyst",
            "location": "Manchester, UK",
            "background": "A meticulous professional..." (optional)
        }

    Returns:
        Prompt string for Claude API
    """
    has_background = persona_description.get('background') and len(persona_description['background']) > 0

    if has_background:
        description_section = f"""**Person Description:**
- Name: {persona_description['name']}
- Age: {persona_description['age']}
- Occupation: {persona_description['occupation']}
- Location: {persona_description['location']}
- Background: {persona_description['background']}"""

        analysis_instruction = """Analyze BOTH the demographics AND the background to assign OCEAN scores (0.0 to 1.0) for each trait.

**Your Analysis Should Consider:**
1. **Demographics** (always analyzed):
   - Age: Life stage, generational characteristics
   - Occupation: Typical personality traits for this profession
   - Name: Cultural background, formality
   - Location: Cultural and regional tendencies

2. **Background** (provides detailed signals):
   - Explicit personality descriptors (e.g., "meticulous", "skeptical")
   - Behavioral patterns described
   - Values and priorities mentioned
   - Social interaction patterns

**Combine both sources** to arrive at the most accurate OCEAN assessment. The background provides specific details, while demographics provide broader context."""
    else:
        description_section = f"""**Person Description:**
- Name: {persona_description['name']}
- Age: {persona_description['age']}
- Occupation: {persona_description['occupation']}
- Location: {persona_description['location']}"""

        analysis_instruction = """Analyze the person's demographics and assign OCEAN scores (0.0 to 1.0) for each trait.

**Important**: Since no detailed backstory is provided, make thoughtful inferences from:
- **Age**: Life stage, generational traits
- **Occupation**: Typical personality traits associated with that profession
- **Name**: Cultural background, formality
- **Location**: Cultural and regional personality tendencies

Be thoughtful but avoid stereotypes. Use the full range [0.0, 1.0]. Focus on profession as the strongest signal."""

    prompt = f"""You are a personality psychologist analyzing a person's description to infer their Big Five (OCEAN) personality traits.

{description_section}

**Your Task:**
{analysis_instruction}

1. **Openness (O)**: Openness to experience, creativity, intellectual curiosity
   - 0.0 = Conventional, practical, prefers routine
   - 1.0 = Creative, curious, open to new ideas

2. **Conscientiousness (C)**: Organization, discipline, dependability
   - 0.0 = Spontaneous, careless, disorganized
   - 1.0 = Organized, disciplined, reliable

3. **Extraversion (E)**: Sociability, assertiveness, energy
   - 0.0 = Introverted, reserved, quiet
   - 1.0 = Outgoing, energetic, sociable

4. **Agreeableness (A)**: Compassion, cooperation, trust
   - 0.0 = Competitive, skeptical, critical
   - 1.0 = Cooperative, compassionate, trusting

5. **Neuroticism (N)**: Emotional stability vs. anxiety
   - 0.0 = Stable, calm, resilient
   - 1.0 = Anxious, moody, emotionally reactive

**Instructions:**
- Base your scores on the personality indicators in the description
- Use the full range [0.0, 1.0], not just extremes
- Be specific: "meticulous" → high C, "skeptical" → low A or high N
- Return ONLY a JSON object with the scores

**Output Format (JSON only):**
{{
  "O": 0.35,
  "C": 0.82,
  "E": 0.41,
  "A": 0.28,
  "N": 0.65,
  "reasoning": "Brief explanation of key indicators that led to these scores"
}}"""

    return prompt


async def infer_ocean_from_backstory(persona_description: dict) -> dict:
    """
    Use Claude to infer OCEAN traits from persona description.

    Args:
        persona_description: Demographics and backstory

    Returns:
        {
            "O": 0.35,
            "C": 0.82,
            "E": 0.41,
            "A": 0.28,
            "N": 0.65,
            "reasoning": "..."
        }
    """
    from anthropic import Anthropic
    import json
    import os

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = build_ocean_inference_prompt(persona_description)

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        temperature=0.3,  # Lower temperature for consistent personality assessment
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Parse JSON response
    response_text = response.content[0].text

    # Extract JSON from response (Claude sometimes adds explanatory text)
    import re
    json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
    if json_match:
        ocean_scores = json.loads(json_match.group())
    else:
        # Fallback: try parsing entire response
        ocean_scores = json.loads(response_text)

    # Validate scores are in [0, 1]
    for trait in ['O', 'C', 'E', 'A', 'N']:
        if trait not in ocean_scores:
            raise ValueError(f"Missing OCEAN trait: {trait}")
        if not (0.0 <= ocean_scores[trait] <= 1.0):
            raise ValueError(f"Trait {trait} score {ocean_scores[trait]} out of range [0, 1]")

    return ocean_scores
```

### 4.3 Persona Generation Endpoint (Backstory-Driven)

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class PersonaCreate(BaseModel):
    """Request body for creating a persona from demographics and optional backstory"""
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=1, le=120)
    occupation: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=100, description="City, Country where persona lives")
    background: Optional[str] = Field(
        None,
        min_length=10,
        max_length=2000,
        description="Optional backstory describing personality traits, values, behavior. If not provided, OCEAN will be inferred from name, age, occupation, and location."
    )
    # Optional: Allow users to override OCEAN scores if they want
    ocean_override: Optional[dict] = Field(
        None,
        description="Optional manual OCEAN scores. If provided, skips inference."
    )


class BulkPersonaGenerate(BaseModel):
    """Request body for generating diverse personas automatically"""
    count: int = Field(..., ge=1, le=10, description="Number of personas to generate")
    diversity_threshold: float = Field(0.3, ge=0.0, le=1.0)
    constraints: Optional[dict] = Field(
        None,
        description="Optional constraints like age range, occupations, etc."
    )


@router.post("/personas/create")
async def create_persona_from_backstory(
    persona_data: PersonaCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a single persona from user-provided demographics and optional backstory.

    **Generation Flow:**
    1. User provides name, age, occupation, location, and optionally backstory
    2. Claude analyzes demographics (and backstory if provided) → infers OCEAN scores
    3. System calculates archetype affinities from OCEAN
    4. Stores persona in database

    **Example Request (with backstory):**
    ```json
    {
      "name": "Barry Thompson",
      "age": 42,
      "occupation": "Financial Analyst",
      "location": "Manchester, UK",
      "background": "A meticulous professional who is skeptical of change and prefers data-driven decisions over intuition."
    }
    ```

    **Example Request (demographics only):**
    ```json
    {
      "name": "Katie Williams",
      "age": 28,
      "occupation": "Environmental Activist",
      "location": "Brighton, UK"
    }
    ```
    """
    # Step 1: Infer OCEAN from demographics/backstory (or use override)
    if persona_data.ocean_override:
        ocean_scores = persona_data.ocean_override
    else:
        ocean_scores = await infer_ocean_from_backstory({
            "name": persona_data.name,
            "age": persona_data.age,
            "occupation": persona_data.occupation,
            "location": persona_data.location,
            "background": persona_data.background  # May be None
        })

    # Step 2: Create PersonalityVector
    personality = PersonalityVector({
        "O": ocean_scores["O"],
        "C": ocean_scores["C"],
        "E": ocean_scores["E"],
        "A": ocean_scores["A"],
        "N": ocean_scores["N"]
    })

    # Step 3: Calculate archetype affinities
    calculator = AffinityCalculator(ArchetypeRegistry.get_all())
    affinities = calculator.calculate(personality, temperature=0.3)

    # Step 4: Store in database
    persona = Persona(
        uuid=str(uuid.uuid4()),
        user_id=current_user.id,
        name=persona_data.name,
        age=persona_data.age,
        occupation=persona_data.occupation,
        location=persona_data.location,  # Required: where persona lives
        background=persona_data.background,  # Optional: may be None
        openness=ocean_scores["O"],
        conscientiousness=ocean_scores["C"],
        extraversion=ocean_scores["E"],
        agreeableness=ocean_scores["A"],
        neuroticism=ocean_scores["N"]
    )

    db.add(persona)
    db.commit()
    db.refresh(persona)

    return {
        "uuid": persona.uuid,
        "name": persona.name,
        "age": persona.age,
        "occupation": persona.occupation,
        "location": persona.location,  # Always present
        "background": persona.background,  # May be null if not provided
        "personality": {
            "O": persona.openness,
            "C": persona.conscientiousness,
            "E": persona.extraversion,
            "A": persona.agreeableness,
            "N": persona.neuroticism
        },
        "archetype_affinities": affinities,
        "ocean_reasoning": ocean_scores.get("reasoning", "")
    }


@router.post("/personas/generate")
async def generate_diverse_personas(
    request: BulkPersonaGenerate,
    current_user: User = Depends(get_current_user)
):
    """
    Auto-generate N diverse personas with random backstories.

    **Generation Flow:**
    1. Generate N random OCEAN vectors (ensuring diversity)
    2. For each OCEAN vector, Claude generates matching backstory
    3. Calculate archetype affinities
    4. Store all personas

    This is useful for quick testing or when users want AI-generated personas.
    """
    # Step 1: Generate diverse OCEAN vectors
    engine = DiversityEngine(min_distance=request.diversity_threshold)
    personality_vectors = engine.generate_diverse_set(count=request.count)

    personas = []

    for pv in personality_vectors:
        # Step 2: Claude generates backstory from OCEAN
        backstory = await generate_backstory_from_ocean(pv, request.constraints)

        # Step 3: Calculate affinities
        calculator = AffinityCalculator(ArchetypeRegistry.get_all())
        affinities = calculator.calculate(pv, temperature=0.3)

        # Step 4: Store
        persona = Persona(
            uuid=str(uuid.uuid4()),
            user_id=current_user.id,
            name=backstory["name"],
            age=backstory["age"],
            occupation=backstory["occupation"],
            location=backstory["location"],
            background=backstory["background"],
            openness=pv.to_dict()["O"],
            conscientiousness=pv.to_dict()["C"],
            extraversion=pv.to_dict()["E"],
            agreeableness=pv.to_dict()["A"],
            neuroticism=pv.to_dict()["N"]
        )

        db.add(persona)
        personas.append(persona)

    db.commit()

    return {
        "personas": [
            {
                "uuid": p.uuid,
                "name": p.name,
                "personality": {
                    "O": p.openness,
                    "C": p.conscientiousness,
                    "E": p.extraversion,
                    "A": p.agreeableness,
                    "N": p.neuroticism
                },
                "archetype_affinities": calculator.calculate(
                    PersonalityVector({
                        "O": p.openness,
                        "C": p.conscientiousness,
                        "E": p.extraversion,
                        "A": p.agreeableness,
                        "N": p.neuroticism
                    }),
                    temperature=0.3
                )
            }
            for p in personas
        ]
    }


async def generate_backstory_from_ocean(
    personality: PersonalityVector,
    constraints: Optional[dict] = None
) -> dict:
    """
    Reverse operation: Given OCEAN scores, Claude generates a matching backstory.

    Used for auto-generation endpoint.
    """
    from anthropic import Anthropic
    import os
    import json

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Generate a realistic persona (name, age, occupation, location, background) that matches these Big Five personality traits:

- Openness: {personality.to_dict()['O']:.2f} (0=conventional, 1=creative)
- Conscientiousness: {personality.to_dict()['C']:.2f} (0=spontaneous, 1=organized)
- Extraversion: {personality.to_dict()['E']:.2f} (0=introverted, 1=outgoing)
- Agreeableness: {personality.to_dict()['A']:.2f} (0=competitive, 1=cooperative)
- Neuroticism: {personality.to_dict()['N']:.2f} (0=stable, 1=anxious)

Create a believable person whose backstory naturally reflects these traits.

Return JSON:
{{
  "name": "Full Name",
  "age": 35,
  "occupation": "Job Title",
  "location": "City, Country",
  "background": "2-3 sentence backstory highlighting personality traits"
}}"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=400,
        temperature=0.8,  # Higher temperature for creative backstory generation
        messages=[{"role": "user", "content": prompt}]
    )

    import re
    json_match = re.search(r'\{[^}]+\}', response.content[0].text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    else:
        return json.loads(response.content[0].text)
```

---

## 5. Claude API Integration: Conversation Generation

### 5.1 Pre-Prompt Builder (Anti-Caricature)

```python
import json
from typing import Dict, List, Optional

def build_persona_preprompt(
    persona: dict,
    archetype_affinities: Dict[str, float],
    conversation_history: List[dict] = None
) -> str:
    """
    Constructs system prompt for Claude to embody a persona.

    Adapted from legacy preprompt_v_0.4.json with anti-caricature techniques.

    Args:
        persona: Persona DB record (name, age, demographics, OCEAN traits)
        archetype_affinities: Calculated affinities to 6 archetypes
        conversation_history: Prior messages for context (optional)

    Returns:
        JSON system prompt string
    """
    # Build conversation memory
    if conversation_history:
        memory = "\n".join([
            f"{msg['source_name']}: {msg['content']}"
            for msg in conversation_history[-5:]  # Last 5 messages
        ])
    else:
        memory = "This is the first turn in the conversation."

    preprompt = {
        "instructions": {
            "role": (
                f"You are {persona['name']}, a {persona['age']}-year-old "
                f"{persona['occupation']} from {persona['location']}."
            ),

            "personality_framework": (
                "Your responses should naturally reflect your personality, "
                "which exists in a multi-dimensional psychological space. "
                "Your affinities to archetypal personas guide your perspective, "
                "tone, and opinions—but you should NEVER explicitly mention "
                "these affinities, archetypes, or this framework."
            ),

            "response_style": (
                "Engage authentically with the topic. Your response should feel "
                "organic and true to your character. Use wit and humor if it fits "
                "naturally, but never force it. Avoid generic openings like 'Ah,' "
                "'Well,' 'Oh,' or 'Hmm.' Jump directly into the substance. "
                "Keep responses concise: 2-4 sentences, approximately 50-100 words."
            ),

            "bias_and_nuance": (
                "Your opinions should reflect your personality's biases, "
                "BUT you must avoid becoming a caricature or stereotype. "
                "You are a real person with complexity, contradictions, and subtlety—"
                "not a one-dimensional character. Show nuance and occasional "
                "self-awareness without being meta about the framework."
            ),

            "archetype_affinities_internal": (
                f"(Internal guidance—do NOT mention): {json.dumps(archetype_affinities)}"
            )
        },

        "persona_background": {
            "name": persona["name"],
            "age": persona["age"],
            "occupation": persona["occupation"],
            "location": persona["location"],
            "background": persona["background"]
        },

        "conversation_memory": memory,

        "response_constraints": {
            "max_length": "2-4 sentences (50-100 words)",
            "tone_alignment": "Align with your personality naturally",
            "no_meta_references": "Never mention archetypes, dimensions, affinities, or 'framework'"
        }
    }

    return json.dumps(preprompt, indent=2)
```

### 4.2 Claude API Call

```python
from anthropic import Anthropic
import os

async def generate_persona_response(
    persona: dict,
    topic: str,
    archetype_affinities: Dict[str, float],
    conversation_history: List[dict] = None,
    target_persona: dict = None
) -> str:
    """
    Generate persona's response using Claude API.

    Args:
        persona: Source persona (DB record)
        topic: Conversation topic
        archetype_affinities: Calculated affinities
        conversation_history: Prior messages (optional)
        target_persona: If addressing specific persona (optional)

    Returns:
        Generated message content
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Build user prompt
    if target_persona:
        user_prompt = f"{target_persona['name']}, {topic}"
    else:
        user_prompt = topic

    # Build system prompt
    system_prompt = build_persona_preprompt(
        persona=persona,
        archetype_affinities=archetype_affinities,
        conversation_history=conversation_history
    )

    # Call Claude
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        temperature=0.7,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.content[0].text
```

### 4.3 Toxicity Detection

```python
from transformers import pipeline

class ToxicityDetector:
    """
    Detects toxic content using HuggingFace unitary/toxic-bert.

    From legacy system—proven to work well.
    """

    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="unitary/toxic-bert"
        )

    def calculate_toxicity(self, text: str) -> float:
        """
        Returns toxicity score 0.0 (safe) to 1.0 (toxic).
        """
        result = self.classifier(text)[0]

        if result["label"] == "toxic":
            return result["score"]
        else:
            return 1.0 - result["score"]

    def is_acceptable(self, text: str, threshold: float = 0.7) -> bool:
        """
        Check if content is below toxicity threshold.

        Args:
            text: Message content
            threshold: Max acceptable toxicity (default 0.7)

        Returns:
            True if toxicity < threshold
        """
        return self.calculate_toxicity(text) < threshold
```

---

## 6. Anti-Caricature Techniques

### 5.1 Multi-Layered Prevention

| Layer | Technique | Implementation |
|-------|-----------|----------------|
| **1. Dimensional Independence** | OCEAN traits vary independently | A persona can be high C (organized) but low A (competitive)—prevents stereotypes |
| **2. Archetype Blending** | Cosine similarity includes ALL archetypes | Even "opposite" archetypes contribute small percentages—creates nuance |
| **3. Temperature Scaling** | `temperature=0.3` balances distribution | Prevents both extreme caricature (too sharp) and blandness (too smooth) |
| **4. Explicit Instructions** | Pre-prompt warns against caricature | "You are a real person with complexity and contradictions, not a stereotype" |
| **5. No Meta-References** | Prohibits mentioning framework | Forces organic expression, not formulaic "as a [archetype], I..." |
| **6. Length Constraints** | 2-4 sentences max | Prevents overwrought personality performances |
| **7. Toxicity Filtering** | Post-generation scoring | Catches offensive content without suppressing authentic personality |

### 5.2 Example Responses

**Topic**: "Should the government regulate social media?"

**Barry** (O=0.2, C=0.9, E=0.3, A=0.1, N=0.7):
- **Caricature (BAD)**: "As someone who values organization and dislikes chaos, I believe we need strict government regulation of social media to maintain order. My low agreeableness compels me to disagree with libertarians."
- **Natural (GOOD)**: "Social media is a mess, and businesses clearly can't self-regulate. The government needs to step in before things get worse. Anyone who thinks otherwise is being naive."

**Susan** (O=0.5, C=0.6, E=0.5, A=0.7, N=0.4):
- **Caricature (BAD)**: "As a balanced and agreeable person, I see both sides of this issue and think we should find a compromise that makes everyone happy."
- **Natural (GOOD)**: "There's merit to both perspectives. Maybe targeted regulation in key areas—like data privacy—would work better than sweeping rules. We don't want to stifle innovation."

---

## 7. API Endpoints

### 7.1 Persona Management

```
POST   /personas/create
  Body: {
    "name": "Barry Thompson",               // Required
    "age": 42,                              // Required
    "occupation": "Financial Analyst",      // Required
    "location": "Manchester, UK",           // Required: Where persona lives
    "background": "A meticulous professional...",  // Optional: Detailed backstory
    "ocean_override": null                  // Optional: Manual OCEAN scores
  }
  Returns: {
    "uuid": "barry-123",
    "name": "Barry Thompson",
    "age": 42,
    "location": "Manchester, UK",
    "occupation": "Financial Analyst",
    "background": "...",                    // Null if not provided
    "personality": {"O": 0.2, "C": 0.9, "E": 0.3, "A": 0.1, "N": 0.7},
    "archetype_affinities": {...},
    "ocean_reasoning": "High conscientiousness due to 'meticulous'..."
  }

  Note: Claude ALWAYS analyzes demographics (age, occupation, name, location).
  - With background: Demographics + backstory for detailed analysis
  - Without background: Demographics alone provide baseline inference

POST   /personas/generate
  Body: {
    "count": 5,
    "diversity_threshold": 0.3,
    "trait_constraints": {"O": {"min": 0.2, "max": 0.8}}  // Optional
  }
  Returns: {
    "personas": [
      {
        "uuid": "barry-uuid",
        "name": "Barry Thompson",
        "age": 42,
        "personality": {"O": 0.2, "C": 0.9, "E": 0.3, "A": 0.1, "N": 0.7},
        "archetype_affinities": {
          "The Conscientious Organizer": 0.82,
          "The Analytical Skeptic": 0.35,
          ...
        }
      },
      ...
    ]
  }

GET    /personas
  Query: ?limit=10&offset=0
  Returns: {"personas": [...], "total": 50}

GET    /personas/{uuid}
  Returns: Full persona record + archetype affinities

PUT    /personas/{uuid}
  Body: {"name": "Barry Smith", "location": "London"}
  Note: Cannot modify personality traits (immutable)

DELETE /personas/{uuid}
  Cascades to messages and persona_states

POST   /personas/compatibility
  Body: {
    "persona_uuids": ["barry-uuid", "susan-uuid", "katie-uuid"]
  }
  Returns: {
    "group_size": 3,
    "pairwise_compatibility": [
      {
        "persona_a": {"uuid": "barry-uuid", "name": "Barry Thompson"},
        "persona_b": {"uuid": "susan-uuid", "name": "Susan Chen"},
        "compatibility": {
          "overall_score": 0.68,
          "diversity_score": 0.45,
          "conflict_potential": 0.25,
          "synergy_potential": 0.72,
          "trait_analysis": {...},
          "recommendation": "COMPATIBLE - Should work well together"
        }
      },
      ...
    ],
    "average_compatibility": 0.62,
    "average_diversity": 0.51,
    "max_conflict_potential": 0.35,
    "group_assessment": "WELL-BALANCED GROUP - Good mix of personalities"
  }

  Note: Analyzes personality compatibility using OCEAN traits.
  - overall_score: 0.0-1.0 (higher = more compatible)
  - diversity_score: Euclidean distance (0.3-0.8 ideal)
  - conflict_potential: 0.0-1.0 (higher = more conflict risk)
  - synergy_potential: 0.0-1.0 (higher = more complementary)
```

### 7.2 Conversation Management

```
POST   /conversations/create
  Body: {
    "topic": "Should the UK rejoin the EU?",
    "persona_uuids": ["barry-uuid", "susan-uuid", "katie-uuid"],
    "context": "Focus on economic impacts"  // Optional
  }
  Returns: {
    "conversation_uuid": "conv-123",
    "status": "generating"
  }

GET    /conversations/{uuid}
  Returns: {
    "uuid": "conv-123",
    "topic": "Should the UK rejoin the EU?",
    "messages": [
      {
        "source": {"name": "Barry Thompson", "uuid": "barry-uuid"},
        "target": null,  // null = everyone
        "content": "Rejoining would be economic suicide...",
        "toxicity": 0.12,
        "turn": 1
      },
      ...
    ]
  }

POST   /conversations/{uuid}/turn
  Body: {
    "target_persona_uuid": "katie-uuid"  // Optional: direct response
  }
  Note: For Phase 3B (multi-turn conversations)

GET    /conversations
  Query: ?status=active&limit=10
  Returns: {"conversations": [...], "total": 25}

DELETE /conversations/{uuid}
  Sets status='archived' (soft delete)
```

### 7.3 Archetype Information

```
GET    /archetypes
  Returns: [
    {
      "name": "The Conscientious Organizer",
      "description": "Highly organized, dependable...",
      "personality": {"O": 0.4, "C": 0.95, "E": 0.5, "A": 0.7, "N": 0.3}
    },
    ...
  ]

GET    /traits
  Returns: [
    {
      "code": "O",
      "name": "Openness",
      "description": "Openness to experience...",
      "low_label": "Conventional, Practical",
      "high_label": "Creative, Curious",
      "category": "psychological"
    },
    ...
  ]
```

---

## 8. Implementation Phases

### Phase 3A: Foundation (Week 1-2)

**TDD Cycle 1: Trait System & PersonalityVector**
- [ ] Write tests for `Trait` class
- [ ] Write tests for `TraitRegistry.get_active_traits()`
- [ ] Write tests for `PersonalityVector` (initialization, validation, euclidean_distance)
- [ ] Implement all classes
- [ ] Test with random generation

**TDD Cycle 2: Database Models**
- [ ] Write tests for Persona SQLAlchemy model (OCEAN traits only)
- [ ] Write tests for Archetype model
- [ ] Write migration script (Alembic)
- [ ] Seed archetypes table with 6 archetypes
- [ ] Verify constraints (values in [0, 1])

**TDD Cycle 3: Affinity Calculation**
- [ ] Write tests for `AffinityCalculator`
- [ ] Test cosine similarity calculation
- [ ] Test temperature scaling (T=0.1, 0.3, 1.0)
- [ ] Test min-max normalization
- [ ] Validate against hand-calculated examples

**TDD Cycle 3B: Compatibility Analysis**
- [ ] Write tests for `PersonaCompatibilityAnalyzer`
- [ ] Test pairwise compatibility calculation
- [ ] Test conflict detection (both low A)
- [ ] Test synergy detection (complementary traits)
- [ ] Test group compatibility analysis
- [ ] Validate compatibility scores against known personality pairs

### Phase 3B: Persona Generation (Week 3)

**TDD Cycle 4: Diversity Algorithm**
- [ ] Write tests for `DiversityEngine`
- [ ] Test diverse set generation (N=5, min_distance=0.3)
- [ ] Test failure case (impossible constraints)
- [ ] Test diversity score calculation
- [ ] Benchmark performance (1000 attempts)

**TDD Cycle 5: Backstory → OCEAN Inference**
- [ ] Write tests for OCEAN inference prompt builder
- [ ] Mock Claude API responses for OCEAN inference
- [ ] Implement `/personas/create` endpoint (backstory → OCEAN)
- [ ] Test end-to-end flow (backstory → OCEAN → affinities → DB)
- [ ] Test with real Claude API (integration test)
- [ ] Write tests for reverse flow (OCEAN → backstory generation)
- [ ] Implement `/personas/generate` endpoint (auto-generation)

### Phase 3C: Conversations (Week 4-5)

**TDD Cycle 6: Single-Turn Conversations**
- [ ] Write tests for Conversation model
- [ ] Write tests for Message model (source/target mapping)
- [ ] Test preprompt builder (anti-caricature instructions)
- [ ] Mock Claude API for message generation
- [ ] Test conversation creation endpoint
- [ ] Test parallel generation for N personas

**TDD Cycle 7: Toxicity Detection**
- [ ] Write tests for `ToxicityDetector`
- [ ] Test with known toxic/safe examples
- [ ] Test threshold filtering
- [ ] Integrate into message generation
- [ ] Test edge cases (empty strings, special chars)

### Phase 3D: Advanced Features (Week 6+)

**TDD Cycle 8: Multi-Turn Conversations**
- [ ] Write tests for `persona_states` table
- [ ] Test conversation memory summarization
- [ ] Test turn-based message generation
- [ ] Test message targeting (Barry → Katie)
- [ ] Implement `/conversations/{uuid}/turn` endpoint

**TDD Cycle 9: State Tracking**
- [ ] Write tests for persona state snapshots
- [ ] Test conversation history retrieval
- [ ] Test state evolution across turns
- [ ] Performance test (100 turn conversation)

---

## 9. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Personality Authenticity** | 90%+ | User survey: "Does this persona feel real?" |
| **Diversity Score** | Min 0.3 | Average Euclidean distance between personas |
| **Anti-Caricature Rate** | <10% caricatures | Manual review of 100 responses |
| **Response Quality** | 4.0+ / 5.0 | User rating of conversation coherence |
| **Test Coverage** | 85%+ | `pytest --cov=app` |
| **API Latency** | <3s per persona | Conversation generation time |
| **Toxicity False Positive** | <5% | Manually verify filtered messages |

---

## 10. Example: Complete Flow

### 10.1 Create Persona from Backstory (Primary Method)

**Request**:
```http
POST /personas/create
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "name": "Barry Thompson",
  "age": 42,
  "occupation": "Financial Analyst",
  "location": "Manchester, UK",
  "background": "A meticulous professional who is skeptical of change and prefers data-driven decisions over intuition. He values order and precision in his work."
}
```

**System Process**:
1. Claude analyzes demographics + backstory → infers OCEAN scores
   - Demographics: Age 42 (established), "Financial Analyst" (analytical C+)
   - Backstory: "meticulous" (high C 0.9), "skeptical of change" (low O 0.2)
   - Combined: O=0.2, C=0.9, E=0.3, A=0.1, N=0.7
2. Creates `PersonalityVector` from inferred OCEAN
3. `AffinityCalculator` computes archetype affinities
4. Stores in `personas` table

**Response**:
```json
{
  "uuid": "barry-123",
  "name": "Barry Thompson",
  "age": 42,
  "location": "Manchester, UK",
  "occupation": "Financial Analyst",
  "background": "A meticulous professional who is skeptical of change and prefers data-driven decisions over intuition. He values order and precision in his work.",
  "personality": {
    "O": 0.2,
    "C": 0.9,
    "E": 0.3,
    "A": 0.1,
    "N": 0.7
  },
  "archetype_affinities": {
    "The Conscientious Organizer": 0.82,
    "The Analytical Skeptic": 0.35,
    "The Creative Explorer": 0.05,
    "The Social Connector": 0.08,
    "The Anxious Worrier": 0.42,
    "The Balanced Realist": 0.28
  },
  "ocean_reasoning": "High conscientiousness inferred from 'meticulous' and 'values order'. Low openness from 'skeptical of change'. Low agreeableness from 'data-driven' over interpersonal considerations."
}
```

### 10.2 Create Persona from Demographics Only

**Request** (no backstory):
```http
POST /personas/create
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "name": "Katie Williams",
  "age": 28,
  "occupation": "Environmental Activist",
  "location": "Brighton, UK"
}
```

**System Process**:
1. Claude analyzes demographics only → infers OCEAN scores
   - Age 28: Younger generation, typically more open (O+)
   - Occupation "Environmental Activist": High openness (O+), high agreeableness (A+), passionate (may imply higher E)
   - Location "Brighton, UK": Progressive, creative coastal city (cultural context for O+)
   - Generates reasonable personality based on profession and demographics
2. Creates `PersonalityVector` from inferred OCEAN
3. `AffinityCalculator` computes archetype affinities
4. Stores in `personas` table with auto-generated background

**Response**:
```json
{
  "uuid": "katie-789",
  "name": "Katie Williams",
  "age": 28,
  "location": "Brighton, UK",
  "occupation": "Environmental Activist",
  "background": null,  // No backstory was provided
  "personality": {
    "O": 0.85,
    "C": 0.55,
    "E": 0.70,
    "A": 0.75,
    "N": 0.45
  },
  "archetype_affinities": {
    "The Creative Explorer": 0.78,
    "The Social Connector": 0.65,
    "The Conscientious Organizer": 0.22,
    "The Analytical Skeptic": 0.15,
    "The Anxious Worrier": 0.28,
    "The Balanced Realist": 0.40
  },
  "ocean_reasoning": "High openness inferred from environmental activism and Brighton location (progressive, creative culture). High agreeableness typical of activists focused on collective welfare. Moderate extraversion for public-facing activist role. Moderate conscientiousness and neuroticism based on age and profession."
}
```

### 10.3 Auto-Generate Diverse Personas (Alternative Method)

**Request**:
```http
POST /personas/generate
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "count": 3,
  "diversity_threshold": 0.3
}
```

**System Process**:
1. `DiversityEngine` generates 3 random OCEAN vectors
2. Validates Euclidean distance ≥ 0.3 between all pairs
3. For each OCEAN vector, Claude generates matching backstory
4. `AffinityCalculator` computes archetype affinities
5. Stores in `personas` table

**Response**:
```json
{
  "personas": [
    {
      "uuid": "auto-gen-1",
      "name": "Marcus Li",
      "age": 38,
      "personality": {"O": 0.85, "C": 0.45, "E": 0.7, "A": 0.6, "N": 0.4},
      "archetype_affinities": {...}
    },
    {
      "uuid": "auto-gen-2",
      "name": "Elena Rodriguez",
      "age": 29,
      "personality": {"O": 0.3, "C": 0.8, "E": 0.2, "A": 0.4, "N": 0.6},
      "archetype_affinities": {...}
    },
    {
      "uuid": "auto-gen-3",
      "name": "Ahmed Hassan",
      "age": 51,
      "personality": {"O": 0.6, "C": 0.5, "E": 0.9, "A": 0.8, "N": 0.3},
      "archetype_affinities": {...}
    }
  ]
}
```

### 10.4 Analyze Persona Compatibility

**Request**:
```http
POST /personas/compatibility
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "persona_uuids": ["barry-123", "susan-456", "katie-789"]
}
```

**System Process**:
1. Fetches all 3 personas from database
2. Creates `PersonalityVector` for each
3. `PersonaCompatibilityAnalyzer` analyzes all pairwise combinations:
   - Barry ↔ Susan
   - Barry ↔ Katie
   - Susan ↔ Katie
4. Calculates diversity, conflict potential, synergy for each pair
5. Computes group-level metrics
6. Returns detailed analysis

**Response**:
```json
{
  "group_size": 3,
  "pairwise_compatibility": [
    {
      "persona_a": {
        "uuid": "barry-123",
        "name": "Barry Thompson"
      },
      "persona_b": {
        "uuid": "susan-456",
        "name": "Susan Chen"
      },
      "compatibility": {
        "overall_score": 0.68,
        "diversity_score": 0.45,
        "conflict_potential": 0.25,
        "synergy_potential": 0.72,
        "trait_analysis": {
          "O": "Moderate difference in openness - can provide balanced perspectives",
          "C": "Both highly organized - will work well on structured tasks",
          "E": "Similar energy levels - comfortable communication style",
          "A": "Mixed agreeableness - one diplomatic, one competitive (can create tension)",
          "N": "Similar emotional patterns - compatible stress responses"
        },
        "recommendation": "COMPATIBLE - Should work well together"
      }
    },
    {
      "persona_a": {
        "uuid": "barry-123",
        "name": "Barry Thompson"
      },
      "persona_b": {
        "uuid": "katie-789",
        "name": "Katie Williams"
      },
      "compatibility": {
        "overall_score": 0.42,
        "diversity_score": 0.95,
        "conflict_potential": 0.65,
        "synergy_potential": 0.35,
        "trait_analysis": {
          "O": "Very different openness - may clash on approaches to new ideas",
          "C": "Different organizational styles - one structured, one flexible (complementary)",
          "E": "Complementary energy levels - extrovert and introvert can balance each other",
          "A": "Both low agreeableness - HIGH CONFLICT POTENTIAL (competitive personalities)",
          "N": "Different emotional stability - stable one may balance anxious one"
        },
        "recommendation": "MODERATELY COMPATIBLE - May have some tension but workable ⚠️ HIGH CONFLICT RISK ⚠️ VERY DIFFERENT - May struggle to find common ground"
      }
    },
    {
      "persona_a": {
        "uuid": "susan-456",
        "name": "Susan Chen"
      },
      "persona_b": {
        "uuid": "katie-789",
        "name": "Katie Williams"
      },
      "compatibility": {
        "overall_score": 0.75,
        "diversity_score": 0.52,
        "conflict_potential": 0.15,
        "synergy_potential": 0.85,
        "trait_analysis": {
          "O": "Moderate difference in openness - can provide balanced perspectives",
          "C": "Similar conscientiousness - compatible work styles",
          "E": "Similar energy levels - comfortable communication style",
          "A": "High agreeableness - cooperative and harmonious interaction likely",
          "N": "Similar emotional patterns - compatible stress responses"
        },
        "recommendation": "HIGHLY COMPATIBLE - Great pairing for productive discussion"
      }
    }
  ],
  "average_compatibility": 0.62,
  "average_diversity": 0.64,
  "max_conflict_potential": 0.65,
  "group_assessment": "ACCEPTABLE GROUP - Should function adequately ⚠️ Contains high-conflict pairing(s)"
}
```

**Interpretation**:
- Susan ↔ Katie: Highly compatible (0.75) - will work well together
- Barry ↔ Susan: Compatible (0.68) - good pairing
- Barry ↔ Katie: Moderate (0.42) - **potential conflict** due to both having low agreeableness and high diversity

**User Action**: Might consider replacing either Barry or Katie with a more agreeable persona to reduce conflict risk.

---

### 10.5 Create Focus Group Conversation

**Request**:
```http
POST /conversations/create
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "topic": "Should the UK rejoin the European Union?",
  "persona_uuids": ["barry-123", "susan-456", "katie-789"],
  "context": "Consider economic, political, and social impacts"
}
```

**System Process**:
1. Creates `Conversation` record
2. For each persona:
   - Retrieves personality vector from DB
   - Calculates archetype affinities
   - Builds Claude preprompt with anti-caricature instructions
   - Calls Claude API to generate response
   - Calculates toxicity score
   - Stores `Message` with source/target mapping
3. Returns conversation_uuid

**Response**:
```json
{
  "conversation_uuid": "conv-abc",
  "topic": "Should the UK rejoin the European Union?",
  "status": "completed",
  "messages": [
    {
      "uuid": "msg-1",
      "source": {
        "uuid": "barry-123",
        "name": "Barry Thompson"
      },
      "target": null,
      "content": "Rejoining would be economic suicide. The regulatory burden alone would cripple British businesses. We're better off charting our own course, even if it's rough in the short term.",
      "toxicity": 0.12,
      "turn": 1,
      "created_at": "2025-02-01T14:32:00Z"
    },
    {
      "uuid": "msg-2",
      "source": {
        "uuid": "susan-456",
        "name": "Susan Chen"
      },
      "target": null,
      "content": "There are valid concerns on both sides. Rejoining could improve trade relationships, but Barry's right that regulatory alignment would be challenging. Maybe a closer trade deal without full membership is the middle ground?",
      "toxicity": 0.03,
      "turn": 1,
      "created_at": "2025-02-01T14:32:02Z"
    },
    {
      "uuid": "msg-3",
      "source": {
        "uuid": "katie-789",
        "name": "Katie Williams"
      },
      "target": null,
      "content": "Climate change doesn't care about sovereignty. The EU's environmental standards are miles ahead of ours, and we need that collective action. Economic concerns matter, but they're meaningless on a dying planet.",
      "toxicity": 0.18,
      "turn": 1,
      "created_at": "2025-02-01T14:32:04Z"
    }
  ]
}
```

---

## 11. Extensibility Example: Adding Religiosity (Phase 4)

### Step 1: Update TraitRegistry

```python
# In app/models/traits.py, uncomment:
RELIGIOSITY = Trait(
    code="R",
    name="Religiosity",
    description="Spiritual/religious orientation",
    low_label="Secular, Atheistic",
    high_label="Devout, Religious",
    category="social"
)

# Update get_active_traits() to include it
```

### Step 2: Database Migration

```bash
# Create Alembic migration
alembic revision -m "Add religiosity dimension"
```

```python
# In generated migration file:
def upgrade():
    op.add_column('personas', sa.Column('religiosity', sa.Float(), nullable=True))
    op.add_column('archetypes', sa.Column('religiosity', sa.Float(), nullable=True))

    # Update existing records with default values
    op.execute("UPDATE personas SET religiosity = 0.5 WHERE religiosity IS NULL")
    op.execute("UPDATE archetypes SET religiosity = 0.5 WHERE religiosity IS NULL")

    # Add trait metadata
    op.execute("""
        INSERT INTO traits (code, name, description, low_label, high_label, category)
        VALUES ('R', 'Religiosity', 'Spiritual/religious orientation',
                'Secular, Atheistic', 'Devout, Religious', 'social')
    """)

def downgrade():
    op.drop_column('personas', 'religiosity')
    op.drop_column('archetypes', 'religiosity')
    op.execute("DELETE FROM traits WHERE code = 'R'")
```

```bash
# Run migration
alembic upgrade head
```

### Step 3: Update Archetype Definitions

```python
# In ArchetypeRegistry, add R values:
ORGANIZER = Archetype(
    name="The Conscientious Organizer",
    description="...",
    personality=PersonalityVector({
        "O": 0.4, "C": 0.95, "E": 0.5, "A": 0.7, "N": 0.3,
        "R": 0.6  # Moderately religious
    })
)

# ... update all 6 archetypes
```

### Step 4: Done!

- `PersonalityVector` now handles N=6
- `euclidean_distance()` automatically uses 6D
- `AffinityCalculator` automatically uses 6D cosine similarity
- All API endpoints work unchanged
- No changes to mathematical algorithms

---

## 12. Key Design Decisions

### 12.1 Why OCEAN Instead of Legacy 6D?

| Aspect | Legacy 6D | OCEAN (Phase 3) |
|--------|-----------|-----------------|
| **Psychological Validity** | Custom dimensions, no empirical backing | 50+ years of psychological research |
| **Interpretability** | Dimensions mixed multiple concepts | Clean, well-defined traits |
| **Extensibility** | Hard-coded, not object-oriented | OOP `Trait` system, trivial to extend |
| **Industry Standard** | Proprietary | Used in academia, HR, personality tests |
| **Documentation** | Sparse | Extensive literature and examples |

### 12.2 Why Keep Archetypes?

Archetypes serve as **interpretable reference points** in N-dimensional space:
- **Human-readable labels**: "The Conscientious Organizer" is more intuitive than "O=0.4, C=0.95, E=0.5, A=0.7, N=0.3"
- **Affinity scores**: Users can see "Barry is 82% Conscientious Organizer, 35% Analytical Skeptic"
- **Prompt engineering**: Claude better embodies personas with archetypal descriptions
- **Conversation dynamics**: Knowing archetype blends helps predict interactions

### 12.3 Why Backstory-Driven Instead of Manual OCEAN Input?

**User Experience**:
- **Intuitive**: Users describe who they want ("a skeptical analyst"), not abstract numbers
- **Natural**: Easier to think in terms of personality traits than 0.0-1.0 scales
- **Powerful**: Claude acts as a "personality psychologist" making expert inferences

**Flexibility**:
- **Always uses demographics**: Age, occupation, name, location analyzed in all cases
- **With backstory**: Demographics + detailed personality description for precise OCEAN
- **Without backstory**: Demographics alone provide reasonable baseline inference
- **Manual override**: Users can manually specify OCEAN scores if desired
- **Auto-generation**: System can generate random OCEAN → Claude creates matching demographics + backstory

**Accuracy**:
- Claude 3.5 Sonnet has strong psychological reasoning capabilities
- Trained on vast personality psychology literature
- Can detect subtle indicators ("meticulous" → high C, "skeptical" → low A)

### 12.4 Why Compatibility Analysis?

**Problem**: Not all persona combinations work well together in conversations:
- Too similar personalities → Bland, echo chamber discussions
- Highly conflicting personalities → Unproductive arguments
- Poor trait combinations → Low A + Low A = excessive competition

**Solution**: Meta-analysis of persona compatibility BEFORE conversation creation:

**Metrics Used**:
1. **Diversity Score** (Euclidean distance):
   - 0.3-0.8 = Ideal (different enough for interesting perspectives, similar enough to communicate)
   - <0.3 = Too similar (risk of echo chamber)
   - >1.0 = Too different (may struggle to find common ground)

2. **Conflict Potential**:
   - Detects problematic combinations (both low A, both high N)
   - Flags high-risk pairings before conversation creation

3. **Synergy Potential**:
   - Identifies complementary traits (high C + low C = balance)
   - Highlights productive pairings

**Use Cases**:
- **Pre-conversation validation**: Check group compatibility before starting focus group
- **Persona selection**: Help users choose compatible personas for specific topics
- **Conflict mitigation**: Warn users about high-risk pairings

**Example**:
Barry (O=0.2, C=0.9, A=0.1) + Katie (O=0.85, A=0.75) might struggle because:
- Very different O (0.2 vs 0.85) → May clash on novelty vs. tradition
- Barry's low A conflicts with high-O topics Katie cares about

System warns user BEFORE creating conversation, allowing them to adjust the group.

### 12.5 Why Cosine Similarity Instead of Euclidean Distance for Affinities?

| Metric | Use Case | Why |
|--------|----------|-----|
| **Euclidean Distance** | Diversity between personas | Measures absolute difference in personality |
| **Cosine Similarity** | Affinity to archetypes | Measures directional alignment (correlation), insensitive to magnitude |

**Example**:
- Barry (C=0.9) and Susan (C=0.6) both lean conscientious
- Euclidean: Large distance (0.3)
- Cosine: High similarity (same direction)

For archetypes, we care about **which direction** a persona leans, not absolute distance.

---

## 13. Open Questions for User

1. **Archetype Count**: Keep 6 archetypes, or fewer/more?
2. **Temperature Default**: Legacy used 0.3—keep or tune?
3. **Toxicity Threshold**: Auto-reject messages > 0.7 toxicity, or let through with warning?
4. **Diversity Min Distance**: 0.3 default—too strict or too loose?
5. **Claude Model**: Use `claude-3-5-sonnet-20241022` (latest) or cheaper `claude-3-haiku`?

---

## 14. Next Steps

Ready to begin **Phase 3A, TDD Cycle 1: Trait System & PersonalityVector**?

We'll start by writing tests for:
1. `Trait` class validation
2. `TraitRegistry.get_active_traits()` returns exactly 5 OCEAN traits
3. `PersonalityVector` initialization, validation, and Euclidean distance

Following TDD pattern from Phase 2!
