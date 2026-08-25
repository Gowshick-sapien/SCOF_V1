import React from "react";
import { useDashboardState } from "../hooks/useDashboardState";
import { useAgentActivity } from "../hooks/useAgentActivity";
import { useDecisions } from "../hooks/useDecisions";
import "./LiveEventsViewer.css";

export const LiveEventsViewer: React.FC = () => {
  const dashboard = useDashboardState();
  const activities = useAgentActivity();
  const decisions = useDecisions();

  return (
    <div className="events-panel">
      <h2>Live Events Diagnostic</h2>
      <hr />
      
      <div className="section">
        <h3>Dashboard State</h3>
        {dashboard ? (
          <pre>{JSON.stringify(dashboard, null, 2)}</pre>
        ) : (
          <span className="empty">Waiting for dashboard updates...</span>
        )}
      </div>

      <div className="section">
        <h3>Agent Activity</h3>
        {activities.length > 0 ? (
          <table className="activity-table">
            <thead>
              <tr>
                <th>Agent</th>
                <th>Status</th>
                <th>Latency (ms)</th>
                <th>Scenario</th>
              </tr>
            </thead>
            <tbody>
              {activities.map((a, i) => (
                <tr key={i}>
                  <td>{a.agent_id}</td>
                  <td className={`status-${a.status.toLowerCase()}`}>{a.status}</td>
                  <td>{a.latency_ms ?? "-"}</td>
                  <td title={a.scenario_id}>{a.scenario_id.split("-")[0]}...</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <span className="empty">Waiting for agent activity...</span>
        )}
      </div>

      <div className="section">
        <h3>Decisions & Orchestration</h3>
        {decisions.length > 0 ? (
          <ul className="decision-list">
            {decisions.map((d, i) => (
              <li key={i}>
                {d.type === "completed" ? (
                  <>
                    <strong className="status-completed">COMPLETED</strong> - 
                    Method: {d.payload.decision_record.decision_method}, 
                    Rec: {d.payload.decision_record.final_recommendation} 
                    (Conf: {(d.payload.decision_record.decision_confidence * 100).toFixed(1)}%)
                  </>
                ) : (
                  <>
                    <strong className="status-failed">FAILED</strong> - 
                    Scenario: {d.payload.scenario_id}, 
                    Reason: {d.payload.reason}
                  </>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <span className="empty">Waiting for decisions...</span>
        )}
      </div>
    </div>
  );
};
