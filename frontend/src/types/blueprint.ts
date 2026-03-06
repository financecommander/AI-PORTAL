// ── Blueprint Session Types ─────────────────────────────────────────

export type BlueprintSessionStatus = 'draft' | 'validating' | 'executing' | 'completed' | 'failed' | 'paused';

export interface BlueprintNode {
  id: string;
  type: 'workflow' | 'step' | 'parallel' | 'guard' | 'budget' | 'quality_gate' | 'circuit_breaker' | 'if' | 'match' | 'try' | 'finally' | 'for_each';
  label: string;
  position: { x: number; y: number };
  properties: Record<string, unknown>;
  children: string[];
}

export interface BlueprintEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  edge_type?: 'default' | 'conditional' | 'fallback' | 'parallel';
}

export interface BlueprintGraph {
  nodes: BlueprintNode[];
  edges: BlueprintEdge[];
  metadata: Record<string, string>;
}

export interface BlueprintSession {
  session_id: string;
  name: string;
  description: string;
  status: BlueprintSessionStatus;
  orc_source: string;
  graph: BlueprintGraph | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  execution_id?: string;
  validation_errors: string[];
}

export interface CreateBlueprintRequest {
  name: string;
  description?: string;
  orc_source?: string;
  graph?: BlueprintGraph;
}

export interface BlueprintValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface BlueprintExecutionStatus {
  execution_id: string;
  session_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  current_step?: string;
  progress: number;
  total_cost: number;
  started_at: string;
  completed_at?: string;
  results: Record<string, unknown>;
  errors: string[];
}

export interface TritonModel {
  name: string;
  description: string;
  compression_profile: string;
  accuracy: string;
  latency: string;
  size: string;
}
