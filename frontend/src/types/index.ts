// ============================================================================
// User
// ============================================================================

export interface User {
  id: number;
  email: string;
  name: string | null;
  picture_url: string | null;
  is_admin: boolean;
  is_superuser: boolean;
  created_at: string;
}

// ============================================================================
// Persona
// ============================================================================

export type Attitude = "Neutral" | "Sarcastic" | "Comical" | "Somber" | "Confrontational" | "Blunt" | "Cynical";

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
  is_public: boolean;
  view_count: number;
  upvote_count: number;
  is_owner?: boolean;
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
  moderation_status: "approved" | "flagged" | "user";
  toxicity_score: number | null;
  created_at: string;
}

export interface Conversation {
  unique_id: string;
  topic: string;
  turn_count: number;
  max_turns: number;
  is_complete: boolean;
  is_public: boolean;
  is_challenge?: boolean;
  proposal?: string | null;
  challenge_type?: string | null;
  status?: "active" | "pending";
  forked_from_id: string | null;
  view_count: number;
  upvote_count: number;
  is_owner?: boolean;
  created_at: string;
  messages?: ConversationMessage[];
  participants?: {
    persona_id: number;
    persona_name: string | null;
    persona_unique_id: string | null;
    avatar_url?: string | null;
    persuaded_score?: number;
  }[];
}

export interface ConversationCreateRequest {
  topic: string;
  persona_ids: string[];
  is_public?: boolean;
}

export interface ConversationUpdateRequest {
  is_public?: boolean;
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
