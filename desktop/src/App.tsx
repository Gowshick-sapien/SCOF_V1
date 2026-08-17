import "./App.css";
import { ConnectionProvider } from "./state/connection";
import { ConnectionStatus } from "./components/ConnectionStatus";

function App() {
  return (
    <ConnectionProvider>
      <main className="scof-shell">
        <h1>SCOF Operations Console</h1>
        <ConnectionStatus />
      </main>
    </ConnectionProvider>
  );
}

export default App;
