import {
  DashboardState,
  Scenario,
  ScenarioTriggerResponse,
  ScenarioReplayResponse,
  DecisionRecord,
  DecisionLog,
  DecisionConfidence,
  DecisionTrace,
  WhatIfRunResponse,
  WhatIfResult,
  Benchmark,
  Calibration,
  ChatResponse,
  ActiveProfile,
  HealthResponse,
} from "./types";

// Configuration for API base URL
// In development, this points to the local D08 instance
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Custom error class for API errors to preserve backend information
 */
export class ApiError extends Error {
  public status: number;
  public data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/**
 * Base HTTP request handler
 */
async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    const contentType = response.headers.get("content-type");
    const isJson = contentType && contentType.includes("application/json");
    
    let data: any = null;
    if (isJson) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const errorMessage = data?.detail || data?.message || response.statusText;
      throw new ApiError(response.status, errorMessage, data);
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Network errors or parsing issues
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

export const ApiClient = {
  // System Health
  health: () => fetchApi<HealthResponse>("/health"),
  
  // Profile
  getActiveProfile: () => fetchApi<ActiveProfile>("/profile/active"),

  // Dashboard
  getDashboardState: () => fetchApi<DashboardState>("/dashboard/state"),

  // Scenarios
  listScenarios: () => fetchApi<{ scenarios: Scenario[] }>("/scenarios"),
  triggerScenario: (scenarioId: string) => 
    fetchApi<ScenarioTriggerResponse>("/scenarios/trigger", {
      method: "POST",
      body: JSON.stringify({ scenario_id: scenarioId })
    }),
  replayScenario: (eventId: string) => 
    fetchApi<ScenarioReplayResponse>("/scenarios/replay", {
      method: "POST",
      body: JSON.stringify({ event_id: eventId })
    }),

  // Decisions
  listDecisions: () => fetchApi<DecisionRecord[]>("/decisions"),
  getDecisionLog: (decisionId: string) => fetchApi<DecisionLog>(`/decisions/${decisionId}/log`),
  getDecisionConfidence: (decisionId: string) => fetchApi<DecisionConfidence>(`/decisions/${decisionId}/confidence`),
  getDecisionTrace: (decisionId: string) => fetchApi<DecisionTrace>(`/decisions/${decisionId}/trace`),

  // What-If
  runWhatIf: (scenarioId: string, severityOverride?: number) => 
    fetchApi<WhatIfRunResponse>("/whatif/run", {
      method: "POST",
      body: JSON.stringify({ 
        scenario_id: scenarioId,
        severity_override: severityOverride 
      })
    }),
  getWhatIfResult: (whatIfId: string) => fetchApi<WhatIfResult>(`/whatif/${whatIfId}/result`),

  // Evaluation
  getBenchmark: () => fetchApi<Benchmark>("/evaluation/benchmark"),
  getCalibration: () => fetchApi<Calibration>("/evaluation/calibration"),

  // Chat
  queryChat: (query: string, limit?: number) => 
    fetchApi<ChatResponse>("/chat/query", {
      method: "POST",
      body: JSON.stringify({ query, limit })
    })
};
