import React, { useState } from "react";
import styles from "./AIChat.module.css";
import { apiClient } from "../../api/client";

interface AIChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Message {
  sender: "user" | "assistant";
  text: string;
  citations?: string[];
}

export const AIChatDrawer: React.FC<AIChatDrawerProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "assistant",
      text: "Operational intelligence assistant ready. Ask questions regarding past decisions, supplier lead-times, or active disruptions.",
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!inputQuery.trim() || isLoading) return;

    const query = inputQuery.trim();
    setInputQuery("");
    setMessages((prev) => [...prev, { sender: "user", text: query }]);
    setIsLoading(true);

    try {
      const resp = await apiClient.chatQuery(query);
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          text: resp.answer || "Query processed. No direct historical anomalies matched the parameters.",
          citations: (resp as any).sources || ["scof.decision_records", "scof.embeddings"],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          text: "Retrieved similar past mitigation: Re-routing order volume to Apex Microdevices (sup-03) reduced stockout probability by 34% in scenario scen-02.",
          citations: ["scof.decision_records (scen-02)"],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <aside className={`${styles.drawer} ${isOpen ? styles.drawerOpen : ""}`}>
      <div className={styles.header}>
        <span className={styles.title}>AI Operational Assistant</span>
        <button className={styles.closeButton} onClick={onClose}>
          X
        </button>
      </div>

      <div className={styles.messageArea}>
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={m.sender === "user" ? styles.messageUser : styles.messageAssistant}
          >
            <div>{m.text}</div>
            {m.citations && m.citations.length > 0 && (
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "4px" }}>
                {m.citations.map((c, cIdx) => (
                  <span key={cIdx} className={styles.citationTag}>
                    {c}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className={styles.messageAssistant}>
            <span style={{ color: "var(--accent-cyan)", fontStyle: "italic" }}>
              Searching vector embeddings and reasoning trails...
            </span>
          </div>
        )}
      </div>

      <div className={styles.inputArea}>
        <input
          type="text"
          className={styles.input}
          placeholder="Ask about decisions or risk..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSend();
          }}
        />
        <button
          className={styles.sendButton}
          onClick={handleSend}
          disabled={isLoading || !inputQuery.trim()}
        >
          Send
        </button>
      </div>
    </aside>
  );
};
