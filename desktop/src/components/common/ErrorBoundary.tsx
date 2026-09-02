import { Component, ErrorInfo, ReactNode } from "react";
import styles from "./ErrorBoundary.module.css";

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught exception in SCOF Console:", error, errorInfo);
    this.setState({ errorInfo });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className={styles.errorContainer}>
          <div className={styles.icon}>!</div>
          <h3 className={styles.title}>
            {this.props.fallbackTitle || "Operational View Error"}
          </h3>
          <p className={styles.description}>
            An unhandled runtime exception occurred while rendering this view. Diagnostic details have been logged to the operations console.
          </p>

          {this.state.error && (
            <div className={styles.stackTrace}>
              {this.state.error.toString()}
              {this.state.errorInfo?.componentStack}
            </div>
          )}

          <button className={styles.reloadButton} onClick={this.handleReset}>
            Reload Operations Console
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
