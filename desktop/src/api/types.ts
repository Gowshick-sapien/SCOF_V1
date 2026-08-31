// --- D08 REST Models ---

export interface DashboardState {
  active_alerts: any[];
  system_health: string;
  recent_decisions: any[];
  active_disruptions: number;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
}

export interface ScenarioTriggerResponse {
  event_id: string;
  trace_id: string;
  status: string;
}

export interface ScenarioReplayResponse {
  event_id: string;
  trace_id: string;
  status: string;
}

export interface EvidenceItem {
  type: "historical_data" | "model_output" | "graph_query" | "external_signal";
  source: string;
  summary: string;
  reference_id: string;
  query_hash?: string;
}

export interface StructuredClaim {
  agent_id: string;
  scenario_id: string;
  recommendation: string;
  reasoning: string;
  confidence: number;
  low_confidence: boolean;
  priority: "HIGH" | "MEDIUM" | "LOW";
  impact: string;
  evidence: EvidenceItem[];
  timestamp: string;
}

export interface AgentWeightBreakdown {
  stated_confidence: number;
  historical_accuracy: number;
  effective_weight: number;
}

export interface ReasoningStep {
  step_index: number;
  step_type: "CLAIM" | "WEIGHT_REPORT" | "TALLY" | "ESCALATION" | "DECISION";
  content: string;
  data?: Record<string, any>;
}

export interface MeetingLogEntry {
  step_index: number;
  speaker: string;
  statement_type: "CLAIM" | "WEIGHT_REPORT" | "TALLY" | "ESCALATION" | "DECISION";
  content: string;
  timestamp: string;
}

export interface DecisionRecord {
  decision_id: string;
  scenario_id: string;
  trace_id?: string;
  consensus_bundle_id: string;
  source_bundle_id: string;
  decision_method: "CD2F" | "SINGLE_AGENT" | "NAIVE_MAJORITY" | string;
  final_recommendation?: string;
  decision_confidence: number;
  weighted_consensus_stability: number;
  escalation_tier: "FAST_PATH" | "SLOW_PATH" | "HUMAN_ESCALATION";
  escalation_rationale: string;
  agent_weights: Record<string, AgentWeightBreakdown>;
  recommendation_tallies: Record<string, number>;
  reasoning_trail: ReasoningStep[];
  meeting_log_entries: MeetingLogEntry[];
  timestamp: string;
  profile_name: string;
  profile_version: string;
  engine_version: string;
}

// Decision endpoints return wrappers:
export interface DecisionLog {
  meeting_log: MeetingLogEntry[];
}

export interface DecisionConfidence {
  decision_confidence: number;
  weighted_consensus_stability: number;
  agent_weights: Record<string, AgentWeightBreakdown>;
}

export interface DecisionTrace {
  reasoning_trail: ReasoningStep[];
}

export interface WhatIfRunResponse {
  whatif_id: string;
  trace_id: string;
  status: string;
}

export interface WhatIfResult {
  whatif_id: string;
  status: string;
}

export interface Benchmark {
  [key: string]: any;
}

export interface Calibration {
  [key: string]: any;
}

export interface ChatResponse {
  answer: string;
  sources: any[];
}

export interface ActiveProfile {
  name: string;
  version: string;
  description: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  services: Record<string, string>;
}

// --- D08 WebSocket Event Models ---

export interface EventEnvelope<T = any> {
  event_id: string;
  event_type: string;
  schema_version: string;
  producer: string;
  timestamp: string;
  correlation: {
    trace_id: string;
    scenario_id: string;
    profile_version: string;
    request_id?: string;
  };
  payload: T;
}

export interface AgentActivityPayload {
  agent_id: string;
  status: "DISPATCHED" | "COMPLETED" | "FAILED";
  latency_ms?: number;
  scenario_id: string;
  trace_id: string;
  claim?: StructuredClaim;
  error?: string;
  timestamp?: string;
}

export interface DecisionCompletedPayload {
  decision_record: DecisionRecord;
}

export interface OrchestrationFailedPayload {
  scenario_id: string;
  reason: string;
}
