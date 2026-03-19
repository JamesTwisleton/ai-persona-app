// ============================================================================
// User
// ============================================================================

export interface User {
  id: number;
  email: string;
  name: string | null;
  picture_url: string | null;
  is_admin: boolean;
  created_at: string;
}

// ============================================================================
// Persona
// ============================================================================

export type Attitude = "Neutral" | "Sarcastic" | "Comical" | "Somber";

export interface Persona {
  unique_id: string;
  name: string;
  age: number | null;
  gender: string | null;
  description: string | null;
  attitude: Attitude | null;
  ocean_openness: number;
  ocean_conscientiousness: number;
  ocean_extraversion: number;
  ocean_agreeableness: number;
  ocean_neuroticism: number;
  archetype_affinities: Record<string, number>;
  motto: string | null;
  avatar_url: string | null;
  created_at: string;
}

export interface OceanScores {
  openness: number;
  conscientiousness: number;
  extraversion: number;
  agreeableness: number;
  neuroticism: number;
}

export interface PersonaCreateRequest {
  name: string;
  age?: number | null;
  gender?: string | null;
  description?: string | null;
  attitude?: Attitude | null;
}

export interface CompatibilityResult {
  diversity_score: number;
  pairwise_distances: Array<{
    persona_a: string;
    persona_b: string;
    distance: number;
  }>;
  persona_count: number;
}

// ============================================================================
// Archetypes
// ============================================================================

export interface Archetype {
  code: string;
  name: string;
  description: string;
  ocean_vector: Record<string, number>;
}

// ============================================================================
// Conversation
// ============================================================================

export interface ConversationMessage {
  id: number;
  persona_name: string;
  message_text: string;
  turn_number: number;
  moderation_status: "approved" | "flagged";
  toxicity_score: number | null;
  created_at: string;
}

export interface Conversation {
  unique_id: string;
  topic: string;
  turn_count: number;
  max_turns: number;
  is_complete: boolean;
  created_at: string;
  messages?: ConversationMessage[];
}

export interface ConversationCreateRequest {
  topic: string;
  persona_ids: string[];
}

export interface ContinueConversationResponse {
  conversation_unique_id: string;
  turn_number: number;
  new_messages: ConversationMessage[];
  is_complete: boolean;
}

// ============================================================================
// API Error
// ============================================================================

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}
