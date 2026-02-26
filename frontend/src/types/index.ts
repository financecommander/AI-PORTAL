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

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
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
  status: 'running' | 'complete' | 'error';
  agents: PipelineAgent[];
  query: string;
  output?: string;
  total_cost?: number;
  total_tokens?: number;
}

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
