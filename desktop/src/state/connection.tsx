import React, { createContext, useContext, useEffect, useReducer } from "react";
import { wsManager, ConnectionState, WebSocketChannel } from "../api/websocket";
import { ApiClient } from "../api/client";

export type DerivedConnectionStatus =
  | "CONNECTED"
  | "DEGRADED"
  | "RECONNECTING"
  | "OFFLINE_CACHED";

export interface GlobalConnectionState {
  apiHealth: "nominal" | "degraded" | "down" | "checking";
  dashboardWs: ConnectionState;
  decisionsWs: ConnectionState;
  agentsWs: ConnectionState;
  streamsConnected: number;
  isReconnecting: boolean;
  pollingFallbackActive: boolean;
  lastSuccessfulSync: string | null;
  lastError: string | null;
  // Derived state from deterministic precedence hierarchy
  derivedStatus: DerivedConnectionStatus;
  overallStatus: "Connected" | "Degraded" | "Reconnecting" | "Offline";
  statusLabel: string;
  footerTag: string;
  statusColor: string;
  isCached: boolean;
}

type Action =
  | { type: "SET_API_HEALTH"; payload: GlobalConnectionState["apiHealth"] }
  | { type: "SET_WS_STATE"; channel: WebSocketChannel; state: ConnectionState; error?: Error }
  | { type: "SET_POLLING_FALLBACK"; payload: boolean }
  | { type: "CHECK_OVERALL_STATUS" };

function computeDerivedStatus(
  apiHealth: GlobalConnectionState["apiHealth"],
  dashboardWs: ConnectionState,
  decisionsWs: ConnectionState,
  agentsWs: ConnectionState,
  lastSuccessfulSync: string | null,
  pollingFallbackActive: boolean
) {
  const wsStates = [dashboardWs, decisionsWs, agentsWs];
  const streamsConnected = wsStates.filter((s) => s === "connected").length;
  const isReconnecting = wsStates.some(
    (s) => s === "reconnecting" || s === "connecting"
  );

  // Precedence 1 (Highest): OFFLINE_CACHED
  if (
    apiHealth === "down" ||
    (apiHealth === "checking" && streamsConnected === 0 && !lastSuccessfulSync)
  ) {
    return {
      streamsConnected,
      isReconnecting,
      derivedStatus: "OFFLINE_CACHED" as DerivedConnectionStatus,
      overallStatus: "Offline" as const,
      statusLabel: "OFFLINE (CACHED)",
      footerTag: "A2A GATEWAY UNREACHABLE",
      statusColor: "var(--status-critical)",
      isCached: true,
    };
  }

  // Precedence 2: RECONNECTING
  if (apiHealth === "nominal" && isReconnecting && streamsConnected < 3) {
    return {
      streamsConnected,
      isReconnecting,
      derivedStatus: "RECONNECTING" as DerivedConnectionStatus,
      overallStatus: "Reconnecting" as const,
      statusLabel: "RECONNECTING...",
      footerTag: `RECONNECTING EVENT STREAMS (${streamsConnected}/3 CONNECTED)`,
      statusColor: "var(--status-warning)",
      isCached: false,
    };
  }

  // Precedence 3: DEGRADED
  if (apiHealth === "nominal" && streamsConnected < 3 && !isReconnecting) {
    const fallbackText = pollingFallbackActive
      ? "POLLING FALLBACK ACTIVE"
      : "WEBSOCKET DISCONNECTED - REST NOMINAL";
    return {
      streamsConnected,
      isReconnecting,
      derivedStatus: "DEGRADED" as DerivedConnectionStatus,
      overallStatus: "Degraded" as const,
      statusLabel: `STREAMS DEGRADED (${streamsConnected}/3)`,
      footerTag: fallbackText,
      statusColor: "var(--status-warning)",
      isCached: false,
    };
  }

  // Precedence 4 (Nominal Baseline): CONNECTED
  return {
    streamsConnected,
    isReconnecting,
    derivedStatus: "CONNECTED" as DerivedConnectionStatus,
    overallStatus: "Connected" as const,
    statusLabel: "CONNECTED",
    footerTag: "A2A PROTOCOL LIVE",
    statusColor: "var(--status-success)",
    isCached: false,
  };
}

const initialComputed = computeDerivedStatus(
  "checking",
  "disconnected",
  "disconnected",
  "disconnected",
  null,
  false
);

const initialState: GlobalConnectionState = {
  apiHealth: "checking",
  dashboardWs: "disconnected",
  decisionsWs: "disconnected",
  agentsWs: "disconnected",
  lastError: null,
  lastSuccessfulSync: null,
  pollingFallbackActive: false,
  ...initialComputed,
};

function reducer(
  state: GlobalConnectionState,
  action: Action
): GlobalConnectionState {
  const newState = { ...state };

  switch (action.type) {
    case "SET_API_HEALTH":
      newState.apiHealth = action.payload;
      if (action.payload === "nominal") {
        newState.lastSuccessfulSync = new Date().toISOString();
        newState.lastError = null;
      }
      break;

    case "SET_WS_STATE":
      if (action.channel === "/ws/dashboard/state") newState.dashboardWs = action.state;
      else if (action.channel === "/ws/decisions/live") newState.decisionsWs = action.state;
      else if (action.channel === "/ws/agents/activity") newState.agentsWs = action.state;

      if (action.state === "connected") {
        newState.lastSuccessfulSync = new Date().toISOString();
      }

      if (action.error) {
        newState.lastError = action.error.message;
      }
      break;

    case "SET_POLLING_FALLBACK":
      newState.pollingFallbackActive = action.payload;
      break;

    case "CHECK_OVERALL_STATUS":
      break;

    default:
      return state;
  }

  // Re-compute derived connection state via deterministic precedence
  const derived = computeDerivedStatus(
    newState.apiHealth,
    newState.dashboardWs,
    newState.decisionsWs,
    newState.agentsWs,
    newState.lastSuccessfulSync,
    newState.pollingFallbackActive
  );

  return {
    ...newState,
    ...derived,
  };
}

const ConnectionContext = createContext<{
  state: GlobalConnectionState;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export const ConnectionProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    let mounted = true;

    // Check REST API Health
    const checkHealth = async () => {
      try {
        await ApiClient.health();
        if (mounted) dispatch({ type: "SET_API_HEALTH", payload: "nominal" });
      } catch {
        if (mounted) dispatch({ type: "SET_API_HEALTH", payload: "down" });
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Periodic check every 30s

    // Connect WebSocket streams
    const channels: WebSocketChannel[] = [
      "/ws/dashboard/state",
      "/ws/decisions/live",
      "/ws/agents/activity",
    ];

    const unsubs = channels.map((channel) => {
      const unsubscribe = wsManager.subscribeState(channel, (wsState, error) => {
        if (mounted) {
          dispatch({
            type: "SET_WS_STATE",
            channel,
            state: wsState,
            error,
          });
        }
      });

      wsManager.connect(channel);
      return unsubscribe;
    });

    return () => {
      mounted = false;
      clearInterval(interval);
      unsubs.forEach((unsub) => unsub());
      channels.forEach((channel) => wsManager.disconnect(channel));
    };
  }, []);

  return (
    <ConnectionContext.Provider value={{ state, dispatch }}>
      {children}
    </ConnectionContext.Provider>
  );
};

export const useConnection = () => {
  const ctx = useContext(ConnectionContext);
  if (!ctx) throw new Error("useConnection must be used within ConnectionProvider");
  return ctx;
};
