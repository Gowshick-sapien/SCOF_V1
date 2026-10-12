import React, { useEffect, useRef } from "react";
import styles from "./ContextualDrawer.module.css";

export interface ContextualDrawerProps {
  isOpen: boolean;
  title: string;
  badge?: string;
  mode: "docked" | "overlay";
  isDirty?: boolean;
  onClose: () => void;
  onDiscard?: () => void;
  children: React.ReactNode;
}

export const ContextualDrawer: React.FC<ContextualDrawerProps> = ({
  isOpen,
  title,
  badge,
  mode,
  isDirty = false,
  onClose,
  onDiscard,
  children,
}) => {
  const drawerRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Focus preservation and restoration
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement | null;
      if (drawerRef.current && mode === "overlay") {
        drawerRef.current.focus();
      }
    } else {
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    }
  }, [isOpen, mode]);

  // Escape key handler
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        handleCloseRequest();
      }
    };

    window.addEventListener("keydown", handleKeyDown, true);
    return () => {
      window.removeEventListener("keydown", handleKeyDown, true);
    };
  }, [isOpen, isDirty]);

  if (!isOpen) return null;

  const handleCloseRequest = () => {
    if (isDirty) {
      const confirmClose = window.confirm(
        "Draft parameters will be preserved in session memory. Keep draft and close inspector?"
      );
      if (confirmClose) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  const drawerContent = (
    <div
      ref={drawerRef}
      className={`${styles.drawer} ${
        mode === "docked" ? styles.docked : styles.overlay
      }`}
      tabIndex={-1}
      role="dialog"
      aria-modal={mode === "overlay"}
      aria-label={title}
    >
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <h3 className={styles.title}>{title}</h3>
          {badge && <span className={styles.badge}>{badge}</span>}
        </div>
        <div className={styles.headerActions}>
          {isDirty && onDiscard && (
            <button
              className={styles.discardBtn}
              onClick={onDiscard}
              title="Discard draft changes"
              aria-label="Discard draft changes"
            >
              Discard
            </button>
          )}
          <button
            className={styles.closeBtn}
            onClick={handleCloseRequest}
            title="Close Inspector (Esc)"
            aria-label="Close Inspector"
          >
            x
          </button>
        </div>
      </div>

      <div className={styles.body}>{children}</div>
    </div>
  );

  if (mode === "overlay") {
    return (
      <>
        <div
          className={styles.backdrop}
          onClick={handleCloseRequest}
          aria-hidden="true"
        />
        {drawerContent}
      </>
    );
  }

  return drawerContent;
};
