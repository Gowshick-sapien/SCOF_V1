import { useState } from "react";
import "./App.css";
import { ConnectionProvider } from "./state/connection";
import { Sidebar, ViewKey } from "./components/layout/Sidebar";
import { TopBar } from "./components/layout/TopBar";
import { OperationsView } from "./views/Operations/OperationsView";
import { DecisionCenterView } from "./views/DecisionCenter/DecisionCenterView";
import { ScenariosView } from "./views/Scenarios/ScenariosView";
import { AgentCommandView } from "./views/AgentCommand/AgentCommandView";
import { WhatIfLabView } from "./views/WhatIfLab/WhatIfLabView";
import { ReasoningTraceView } from "./views/ReasoningTrace/ReasoningTraceView";
import { EvaluationView } from "./views/Evaluation/EvaluationView";
import { AIChatDrawer } from "./components/chat/AIChatDrawer";

const VIEW_LABELS: Record<ViewKey, string> = {
  operations: "Operational Overview",
  decisions: "Decision Center & Meeting Log",
  scenarios: "Scenario Launcher & Disruptions",
  agents: "Agent Command Center",
  whatif: "What-If Simulation Lab",
  traces: "Reasoning Trace Explorer",
  evaluation: "Evaluation & Benchmarks",
};

function App() {
  const [activeView, setActiveView] = useState<ViewKey>("operations");
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | undefined>();
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);

  const handleSelectDecision = (decisionId: string) => {
    setSelectedDecisionId(decisionId);
    setActiveView("decisions");
  };

  const handleOpenTrace = (decisionId: string) => {
    setSelectedDecisionId(decisionId);
    setActiveView("traces");
  };

  return (
    <ConnectionProvider>
      <div className="appLayout">
        <Sidebar activeView={activeView} onSelectView={setActiveView} />

        <div className="mainArea">
          <TopBar
            currentViewLabel={VIEW_LABELS[activeView]}
            isChatOpen={isChatOpen}
            onToggleChat={() => setIsChatOpen(!isChatOpen)}
          />

          <main className="contentContainer">
            {activeView === "operations" && (
              <OperationsView onSelectDecision={handleSelectDecision} />
            )}
            {activeView === "decisions" && (
              <DecisionCenterView
                selectedDecisionId={selectedDecisionId}
                onOpenTrace={handleOpenTrace}
              />
            )}
            {activeView === "scenarios" && <ScenariosView />}
            {activeView === "agents" && <AgentCommandView />}
            {activeView === "whatif" && <WhatIfLabView />}
            {activeView === "traces" && (
              <ReasoningTraceView selectedDecisionId={selectedDecisionId} />
            )}
            {activeView === "evaluation" && <EvaluationView />}
          </main>

          <AIChatDrawer
            isOpen={isChatOpen}
            onClose={() => setIsChatOpen(false)}
          />
        </div>
      </div>
    </ConnectionProvider>
  );
}

export default App;
