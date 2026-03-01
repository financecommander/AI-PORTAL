import { Component, type ReactNode, type ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--cr-surface, #F8F9FA)',
            padding: 24,
          }}
        >
          <div
            style={{
              maxWidth: 440,
              textAlign: 'center',
              background: '#fff',
              borderRadius: 12,
              padding: '32px 24px',
              border: '1px solid var(--cr-border, #E5E7EB)',
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            }}
          >
            <div style={{ fontSize: 32, marginBottom: 12 }}>Something went wrong</div>
            <p style={{ color: 'var(--cr-text-secondary, #6B7280)', fontSize: 14, lineHeight: 1.5, margin: '0 0 16px' }}>
              An unexpected error occurred. Please refresh the page to continue.
            </p>
            {this.state.error && (
              <pre
                style={{
                  fontSize: 11,
                  color: 'var(--cr-danger, #DC2626)',
                  background: '#FEF2F2',
                  borderRadius: 8,
                  padding: 12,
                  textAlign: 'left',
                  overflow: 'auto',
                  maxHeight: 120,
                  margin: '0 0 16px',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {this.state.error.message}
              </pre>
            )}
            <button
              onClick={() => window.location.reload()}
              style={{
                background: 'var(--cr-green-900, #14532D)',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: '10px 24px',
                fontSize: 14,
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              Reload page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
