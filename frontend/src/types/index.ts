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
