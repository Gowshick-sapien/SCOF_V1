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

export interface BenchmarkMetricRow {
  method: string;
  accuracy: number;
  wcs_stability: number;
  latency_ms: number;
  human_escalation_pct: number;
  cohens_kappa?: number;
  stockout_reduction_pct?: number;
  fill_rate_delta?: number;
  sample_count?: number;
}

export interface CalibrationMetrics {
  sample_count: number;
  recommendation_kappa: number;
  escalation_tier_kappa: number;
  agreement_rate_mean: number;
  fast_path_latency_p50_ms: number;
  fast_path_latency_p90_ms: number;
  slow_path_latency_p50_ms: number;
  stockout_reduction_pct: number;
  fill_rate_delta: number;
}

export interface BenchmarkSummaryResponse {
  benchmark_results: BenchmarkMetricRow[];
  calibration_metrics: CalibrationMetrics;
  status: string;
  eval_run_id: string;
  dataset_name: string;
  timestamp: string;
}

export interface CategoryMetricRow {
  category: string;
  scenario_count: number;
  accuracy: number;
  wcs_stability: number;
  latency_p50_ms: number;
  conflict_intensity: number;
  fast_path_pct: number;
  human_escalation_pct: number;
}

export interface CategoryBenchmarkResponse {
  dataset_name: string;
  total_scenarios: number;
  categories: CategoryMetricRow[];
  status: string;
  timestamp: string;
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
