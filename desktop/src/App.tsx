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
import { ShortcutsModal } from "./components/modals/ShortcutsModal";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import { ConnectionBanner } from "./components/common/ConnectionBanner";
import { NotificationToast } from "./components/common/NotificationToast";

import { useAgentActivity } from "./hooks/useAgentActivity";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";

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
  useAgentActivity();
  const [activeView, setActiveView] = useState<ViewKey>("operations");
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | undefined>();
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState<boolean>(false);

  const handleSelectDecision = (decisionId: string) => {
    setSelectedDecisionId(decisionId);
    setActiveView("decisions");
  };

  const handleOpenTrace = (decisionId: string) => {
    setSelectedDecisionId(decisionId);
    setActiveView("traces");
  };

  const handleEscape = () => {
    if (isShortcutsOpen) setIsShortcutsOpen(false);
    else if (isChatOpen) setIsChatOpen(false);
  };

  useKeyboardShortcuts({
    onSelectView: (view) => setActiveView(view),
    onToggleChat: () => setIsChatOpen((prev) => !prev),
    onToggleShortcutsModal: () => setIsShortcutsOpen((prev) => !prev),
    onEscape: handleEscape,
  });

  return (
    <ConnectionProvider>
      <div className="appLayout">
        <Sidebar activeView={activeView} onSelectView={setActiveView} />

        <div className="mainArea">
          <TopBar
            currentViewLabel={VIEW_LABELS[activeView]}
            isChatOpen={isChatOpen}
            onToggleChat={() => setIsChatOpen(!isChatOpen)}
            onOpenShortcuts={() => setIsShortcutsOpen(true)}
          />

          <ConnectionBanner />

          <main className="contentContainer">
            <ErrorBoundary fallbackTitle={`Error rendering ${VIEW_LABELS[activeView]}`}>
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
            </ErrorBoundary>
          </main>

          <AIChatDrawer
            isOpen={isChatOpen}
            onClose={() => setIsChatOpen(false)}
          />

          <ShortcutsModal
            isOpen={isShortcutsOpen}
            onClose={() => setIsShortcutsOpen(false)}
          />

          <NotificationToast onSelectDecision={handleSelectDecision} />
        </div>
      </div>
    </ConnectionProvider>
  );
}

export default App;
