import React, { createContext, useContext, useEffect, useReducer } from "react";
import { wsManager, ConnectionState, WebSocketChannel } from "../api/websocket";
import { ApiClient } from "../api/client";

interface GlobalConnectionState {
  apiHealth: "nominal" | "degraded" | "down" | "checking";
  dashboardWs: ConnectionState;
  decisionsWs: ConnectionState;
  agentsWs: ConnectionState;
  overallStatus: "Connected" | "Reconnecting" | "Disconnected";
  lastError: string | null;
  lastSuccessfulConnection: string | null;
}

type Action = 
  | { type: "SET_API_HEALTH"; payload: GlobalConnectionState["apiHealth"] }
  | { type: "SET_WS_STATE"; channel: WebSocketChannel; state: ConnectionState; error?: Error }
  | { type: "CHECK_OVERALL_STATUS" };

const initialState: GlobalConnectionState = {
  apiHealth: "checking",
  dashboardWs: "disconnected",
  decisionsWs: "disconnected",
  agentsWs: "disconnected",
  overallStatus: "Disconnected",
  lastError: null,
  lastSuccessfulConnection: null,
};

function reducer(state: GlobalConnectionState, action: Action): GlobalConnectionState {
  const newState = { ...state };

  switch (action.type) {
    case "SET_API_HEALTH":
      newState.apiHealth = action.payload;
      break;
    case "SET_WS_STATE":
      if (action.channel === "/ws/dashboard/state") newState.dashboardWs = action.state;
      else if (action.channel === "/ws/decisions/live") newState.decisionsWs = action.state;
      else if (action.channel === "/ws/agents/activity") newState.agentsWs = action.state;
      
      if (action.error) {
        newState.lastError = action.error.message;
      }
      break;
    case "CHECK_OVERALL_STATUS":
      // Handled globally at the end of reducer
      break;
    default:
      return state;
  }

  // Compute overall status based on current internal states
  const wsStates = [newState.dashboardWs, newState.decisionsWs, newState.agentsWs];
  
  if (wsStates.every(s => s === "connected") && newState.apiHealth === "nominal") {
    newState.overallStatus = "Connected";
    newState.lastSuccessfulConnection = new Date().toISOString();
    newState.lastError = null;
  } else if (wsStates.some(s => s === "reconnecting") || wsStates.some(s => s === "connecting")) {
    newState.overallStatus = "Reconnecting";
  } else {
    newState.overallStatus = "Disconnected";
  }

  return newState;
}

const ConnectionContext = createContext<{
  state: GlobalConnectionState;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export const ConnectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    let mounted = true;
    
    // Poll API Health
    const checkHealth = async () => {
      try {
        await ApiClient.health();
        if (mounted) dispatch({ type: "SET_API_HEALTH", payload: "nominal" });
      } catch (e) {
        if (mounted) dispatch({ type: "SET_API_HEALTH", payload: "down" });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s

    // Connect WebSockets
    const channels: WebSocketChannel[] = [
      "/ws/dashboard/state",
      "/ws/decisions/live",
      "/ws/agents/activity"
    ];

    const unsubs = channels.map(channel => {
      wsManager.connect(channel);
      return wsManager.subscribeState(channel, (wsState, error) => {
        if (mounted) {
          dispatch({ type: "SET_WS_STATE", channel, state: wsState, error });
        }
      });
    });

    return () => {
      mounted = false;
      clearInterval(interval);
      unsubs.forEach(unsub => unsub());
      channels.forEach(channel => wsManager.disconnect(channel));
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
