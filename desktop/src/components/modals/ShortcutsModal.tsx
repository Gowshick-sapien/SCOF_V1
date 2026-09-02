import React from "react";
import styles from "./ShortcutsModal.module.css";

interface ShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ShortcutsModal: React.FC<ShortcutsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h3 className={styles.title}>Control Room Keyboard Shortcuts</h3>
          <button className={styles.closeButton} onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.section}>
            <span className={styles.sectionHeading}>Navigation Hotkeys</span>
            <div className={styles.shortcutGrid}>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>Operations Overview</span>
                <kbd className={styles.kbd}>Ctrl + 1</kbd>
              </div>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>Decision Center</span>
                <kbd className={styles.kbd}>Ctrl + 2</kbd>
              </div>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>Scenario Launcher</span>
                <kbd className={styles.kbd}>Ctrl + 3</kbd>
              </div>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>Agent Command</span>
                <kbd className={styles.kbd}>Ctrl + 4</kbd>
              </div>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>What-If Lab</span>
                <kbd className={styles.kbd}>Ctrl + 5</kbd>
              </div>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>Reasoning Traces</span>
                <kbd className={styles.kbd}>Ctrl + 6</kbd>
              </div>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>Evaluation Matrix</span>
                <kbd className={styles.kbd}>Ctrl + 7</kbd>
              </div>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>AI Assistant Drawer</span>
                <kbd className={styles.kbd}>Ctrl + K</kbd>
              </div>
            </div>
          </div>

          <div className={styles.section}>
            <span className={styles.sectionHeading}>General & Dialog Controls</span>
            <div className={styles.shortcutGrid}>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>Toggle Shortcuts HUD</span>
                <kbd className={styles.kbd}>Shift + ?</kbd>
              </div>
              <div className={styles.shortcutItem}>
                <span className={styles.label}>Dismiss Modal / Drawer</span>
                <kbd className={styles.kbd}>Esc</kbd>
              </div>
            </div>
          </div>
        </div>

        <div className={styles.footer}>
          <span>Press <kbd className={styles.kbd}>Esc</kbd> or click outside to dismiss</span>
        </div>
      </div>
    </div>
  );
};
