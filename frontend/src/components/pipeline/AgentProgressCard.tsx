import { useState, useEffect } from 'react';
import { Check, X, ChevronDown, ChevronUp } from 'lucide-react';

interface AgentProgressCardProps {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  index: number;
  totalAgents: number;
  tokens?: { input: number; output: number };
  cost?: number;
  durationMs?: number;
  output?: string;
}

export default function AgentProgressCard({
  name,
  status,
  index,
  totalAgents,
  tokens,
  cost,
  durationMs,
  output,
}: AgentProgressCardProps) {
  const [expanded, setExpanded] = useState(false);
  const isLast = index === totalAgents - 1;

  const stepCircle = () => {
    const base: React.CSSProperties = {
      width: 32,
      height: 32,
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
      fontSize: '13px',
      fontWeight: 600,
      transition: 'all 300ms',
    };

    if (status === 'complete') {
      return (
        <div style={{ ...base, background: 'var(--cr-green-600)', color: 'var(--cr-text)' }}>
          <Check style={{ width: 16, height: 16 }} />
        </div>
      );
    }
    if (status === 'error') {
      return (
        <div style={{ ...base, background: 'var(--cr-danger)', color: 'var(--cr-text)' }}>
          <X style={{ width: 16, height: 16 }} />
        </div>
      );
    }
    if (status === 'running') {
      return (
        <div
          className="animate-pulse-glow"
          style={{ ...base, border: '2px solid var(--cr-green-600)', color: 'var(--cr-text)' }}
        >
          {index + 1}
        </div>
      );
    }
    // pending
    return (
      <div style={{ ...base, border: '2px dashed var(--cr-border)', color: 'var(--cr-text-dim)' }}>
        {index + 1}
      </div>
    );
  };

  const statusText = () => {
    if (status === 'pending') return <span style={{ color: 'var(--cr-text-dim)', fontSize: '12px' }}>Waiting...</span>;
    if (status === 'running') return <AnimatedDots />;
    if (status === 'error') return <span style={{ color: 'var(--cr-danger)', fontSize: '12px' }}>Failed</span>;
    if (status === 'complete' && tokens && cost != null && durationMs != null) {
      const totalTokens = tokens.input + tokens.output;
      return (
        <span style={{ color: 'var(--cr-text-dim)', fontSize: '12px' }}>
          {totalTokens.toLocaleString()} tokens · ${cost.toFixed(4)} · {(durationMs / 1000).toFixed(1)}s
        </span>
      );
    }
    return null;
  };

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '14px',
          background: 'var(--cr-charcoal-deep)',
          borderRadius: '8px',
          padding: '16px',
        }}
      >
        {stepCircle()}

        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              color: status === 'pending' ? 'var(--cr-text-dim)' : 'var(--cr-text)',
              fontWeight: 500,
              fontSize: '14px',
              marginBottom: '2px',
              transition: 'color 300ms',
            }}
          >
            {name}
          </div>
          {statusText()}
        </div>

        {status === 'complete' && output && (
          <button
            onClick={() => setExpanded(v => !v)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--cr-text-dim)',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {expanded ? <ChevronUp style={{ width: 16, height: 16 }} /> : <ChevronDown style={{ width: 16, height: 16 }} />}
          </button>
        )}
      </div>

      {expanded && output && (
        <div
          style={{
            background: 'var(--cr-charcoal-dark)',
            borderRadius: '0 0 8px 8px',
            padding: '12px 16px',
            maxHeight: '200px',
            overflowY: 'auto',
            marginTop: '-4px',
          }}
        >
          <p style={{ color: 'var(--cr-text-muted)', fontSize: '13px', margin: 0, whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
            {output}
          </p>
        </div>
      )}

      {!isLast && (
        <div
          style={{
            width: '2px',
            height: '16px',
            background: status === 'running' ? 'var(--cr-green-600)' : 'var(--cr-border)',
            margin: '0 auto',
            transition: 'background 300ms',
          }}
        />
      )}
    </div>
  );
}

function AnimatedDots() {
  return (
    <span style={{ color: 'var(--cr-green-400)', fontSize: '12px' }}>
      Analyzing<DotAnimation />
    </span>
  );
}

function DotAnimation() {
  const [dots, setDots] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(d => (d % 3) + 1);
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return <span>{'.'.repeat(dots)}</span>;
}
