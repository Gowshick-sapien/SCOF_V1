import { useEffect } from "react";
import type { ViewKey } from "../components/layout/Sidebar";

interface KeyboardShortcutsOptions {
  onSelectView: (view: ViewKey) => void;
  onToggleChat: () => void;
  onToggleShortcutsModal: () => void;
  onEscape: () => void;
}

const VIEW_SHORTCUTS: Record<string, ViewKey> = {
  "1": "operations",
  "2": "decisions",
  "3": "scenarios",
  "4": "agents",
  "5": "whatif",
  "6": "traces",
  "7": "evaluation",
};

export function useKeyboardShortcuts({
  onSelectView,
  onToggleChat,
  onToggleShortcutsModal,
  onEscape,
}: KeyboardShortcutsOptions) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Do not intercept hotkeys if user is typing inside an input or textarea
      const target = e.target as HTMLElement | null;
      const isInput =
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.isContentEditable;

      if (e.key === "Escape") {
        onEscape();
        return;
      }

      // Allow Ctrl+K or Cmd+K anywhere (even from inputs)
      if ((e.ctrlKey || e.metaKey) && (e.key === "k" || e.key === "K" || e.key === "/")) {
        e.preventDefault();
        onToggleChat();
        return;
      }

      // Shift+? or ? toggles shortcuts modal if not in an input
      if (!isInput && (e.key === "?" || (e.shiftKey && e.key === "/"))) {
        e.preventDefault();
        onToggleShortcutsModal();
        return;
      }

      // Ctrl + [1-7] or Cmd + [1-7] for view switching
      if ((e.ctrlKey || e.metaKey) && VIEW_SHORTCUTS[e.key]) {
        e.preventDefault();
        onSelectView(VIEW_SHORTCUTS[e.key]);
        return;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onSelectView, onToggleChat, onToggleShortcutsModal, onEscape]);
}
