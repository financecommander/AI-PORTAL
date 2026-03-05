// ── Swarm Session Types ─────────────────────────────────────────────

export type CollaborationMode = 'round_table' | 'review_chain' | 'specialist' | 'debate';
export type SessionStatus = 'active' | 'paused' | 'completed' | 'failed';

export interface SwarmSession {
  session_id: string;
  project_name: string;
  description: string;
  mode: CollaborationMode;
  status: SessionStatus;
  participating_castes: string[];
  current_round: number;
  total_cost: number;
  max_rounds: number;
  max_total_cost: number;
  message_count: number;
  created_by: string;
  created_at: string;
}

export interface SessionMessage {
  message_id: string;
  role: 'human' | 'assistant' | 'system';
  content: string;
  caste?: string;
  model_used?: string;
  cost: number;
  latency_ms: number;
  round_number: number;
  created_at: string;
}

export interface CreateSessionRequest {
  project_name: string;
  description: string;
  mode: CollaborationMode;
  team_preset?: string;
  castes?: string[];
  max_rounds?: number;
  max_total_cost?: number;
  created_by?: string;
}

export interface RoundResponse {
  session_id: string;
  round_number: number;
  response_count: number;
  round_cost: number;
  total_cost: number;
  messages: SessionMessage[];
}

export interface SessionDetail extends SwarmSession {
  messages: SessionMessage[];
}

export interface TeamPresets {
  [key: string]: string[];
}

// ── WebSocket Event Types ───────────────────────────────────────────

export interface SwarmWSEvent {
  type: 'new_message' | 'session_update' | 'round_complete' | 'error';
  session_id: string;
  data: Record<string, unknown>;
}
