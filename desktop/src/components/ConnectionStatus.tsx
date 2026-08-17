import React from "react";
import { useConnection } from "../state/connection";
import "./ConnectionStatus.css";

export const ConnectionStatus: React.FC = () => {
  const { state } = useConnection();
  
  const getStatusColor = () => {
    switch (state.overallStatus) {
      case "Connected": return "#4caf50";
      case "Reconnecting": return "#ff9800";
      case "Disconnected": return "#f44336";
    }
  };

  return (
    <div className="connection-panel">
      <h2>D08 Connection</h2>
      <hr />
      <ul>
        <li>
          <span>API</span>
          <span><span className={`status-dot ${state.apiHealth === 'nominal' ? 'green' : 'red'}`}>●</span> {state.apiHealth}</span>
        </li>
        <li>
          <span>Dashboard WS</span>
          <span><span className={`status-dot ${state.dashboardWs === 'connected' ? 'green' : (state.dashboardWs === 'reconnecting' ? 'orange' : 'red')}`}>●</span> {state.dashboardWs}</span>
        </li>
        <li>
          <span>Decisions WS</span>
          <span><span className={`status-dot ${state.decisionsWs === 'connected' ? 'green' : (state.decisionsWs === 'reconnecting' ? 'orange' : 'red')}`}>●</span> {state.decisionsWs}</span>
        </li>
        <li>
          <span>Agents WS</span>
          <span><span className={`status-dot ${state.agentsWs === 'connected' ? 'green' : (state.agentsWs === 'reconnecting' ? 'orange' : 'red')}`}>●</span> {state.agentsWs}</span>
        </li>
      </ul>
      <div className="overall-status">
        <span>Overall</span>
        <strong style={{ color: getStatusColor() }}>● {state.overallStatus}</strong>
      </div>
      {state.lastError && <div className="error-msg">Error: {state.lastError}</div>}
    </div>
  );
};
