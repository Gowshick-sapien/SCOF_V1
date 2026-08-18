import "./App.css";
import { ConnectionProvider } from "./state/connection";
import { ConnectionStatus } from "./components/ConnectionStatus";
import { ProfileStatus } from "./components/ProfileStatus";

function App() {
  return (
    <ConnectionProvider>
      <main className="scof-shell">
        <h1>SCOF Operations Console</h1>
        <div className="shell-grid">
          <ConnectionStatus />
          <ProfileStatus />
        </div>
      </main>
    </ConnectionProvider>
  );
}

export default App;
