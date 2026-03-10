export interface Specialist {
  id: string;
  name: string;
  description: string;
  provider: string;
  model: string;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
  version: number;
}

export interface Attachment {
  filename: string;
  content_type: string;     // MIME type: "image/png", "application/pdf", etc.
  data_base64: string;      // base64-encoded file content (no data: URI prefix)
  size_bytes: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  _id?: string;                 // Stable key for React lists
  attachments?: Attachment[];   // Files attached to this message (user messages only)
  tokens?: { input: number; output: number };
  cost_usd?: number;
  latency_ms?: number;
}

export interface ChatResponse {
  content: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  cost_usd: number;
}

export interface Pipeline {
  name: string;
  description: string;
  agents: string[];
  estimated_cost: number;
}

export interface PipelineAgent {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  input_tokens?: number;
  output_tokens?: number;
  cost_usd?: number;
  duration_ms?: number;
  output?: string;
}

export interface PipelineRun {
  pipeline_id: string;
  pipeline_name?: string;
  status: 'running' | 'complete' | 'error';
  agents: PipelineAgent[];
  query: string;
  output?: string;
  total_cost?: number;
  total_tokens?: number;
  duration_ms?: number;
  created_at?: string;
}

// ── Direct LLM Chat ─────────────────────────────────────────────

export interface LLMModel {
  id: string;
  name: string;
  tier: 'top' | 'mid' | 'budget';
  context?: string;
  description?: string;
  input_price: number;
  output_price: number;
}

export interface LLMProvider {
  id: string;
  name: string;
  models: LLMModel[];
}

export interface LLMModelsResponse {
  providers: LLMProvider[];
}

// ── Usage ───────────────────────────────────────────────────────

export interface UsageLog {
  id: number;
  user_hash: string;
  timestamp: string;
  provider: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number;
  specialist_id?: string;
}

// ── Conversations ────────────────────────────────────────────────

export interface ConversationSummary {
  uuid: string;
  title: string;
  provider: string;
  model: string;
  mode: string;
  specialist_id?: string;
  message_count: number;
  created_at: string;
  updated_at: string;
  preview: string;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ChatMessage[];
}

// ── Console Intelligence ─────────────────────────────────────────

export interface ConsoleHost {
  alias: string;
  hostname: string;
  username: string;
  port: number;
  description: string;
  tags: string[];
}

export interface CommandPlan {
  host: string | null;
  command: string | null;
  explanation: string | null;
  risk: string;
  error: string | null;
}

export interface ConsoleEvent {
  type: 'plan' | 'executing' | 'stdout' | 'stderr' | 'status' | 'error';
  data: Record<string, string | null>;
}

export interface ConsoleEntry {
  id: string;
  input: string;
  plan?: CommandPlan;
  output: string;
  stderr: string;
  status?: string;
  error?: string;
  isRunning: boolean;
  timestamp: Date;
}

// ── LeadOps / Permits ───────────────────────────────────────────

export interface PermitRecord {
  id: number;
  permit_number: string;
  address: string;
  city?: string;
  state?: string;
  zip?: string;
  permit_type: string;
  status?: string;
  issue_date?: string;
  expiration_date?: string;
  estimated_cost?: number;
  lead_score: number | null;
  lead_tier: string;
  ai_tags: string[];
  applicant_name?: string;
  contractor_name?: string;
  owner_name?: string;
  fee_paid?: number;
  work_description?: string;
  ai_property_type?: string;
  ai_project_category?: string;
  ai_summary?: string;
  lead_rationale?: string;
  source_jurisdiction?: string;
}

export interface PermitSearchParams {
  q?: string;
  query?: string;
  city?: string;
  state?: string;
  permit_type?: string;
  status?: string;
  lead_tier?: string;
  date_from?: string;
  date_to?: string;
  min_cost?: number;
  max_cost?: number;
  limit?: number;
  offset?: number;
  sort?: string;
  order?: string;
}

export interface PermitStats {
  total_permits: number;
  active_permits: number;
  expired_permits: number;
  avg_valuation: number;
  avg_lead_score: number;
  top_cities: Array<{ city: string; count: number }>;
  by_type: Array<{ type: string; count: number }>;
  by_tier?: Record<string, number>;
}

