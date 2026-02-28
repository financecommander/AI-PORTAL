import { useState } from 'react';
import { Send } from 'lucide-react';

const EXAMPLE_PROMPTS = [
  'Analyze the financial health of a mid-sized SaaS company',
  'Summarize risks in a venture capital term sheet',
  "Evaluate a startup's competitive positioning in fintech",
];

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isRunning: boolean;
  readOnly?: boolean;
  value?: string;
  estimatedCost?: number;
}

export default function QueryInput({ onSubmit, isRunning, readOnly, value, estimatedCost }: QueryInputProps) {
  const [query, setQuery] = useState(value ?? '');

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (trimmed && !isRunning) onSubmit(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      style={{
        background: 'var(--cr-charcoal-deep)',
        borderRadius: 'var(--cr-radius)',
        padding: '16px',
      }}
    >
      <div style={{ position: 'relative' }}>
        <textarea
          value={readOnly ? (value ?? '') : query}
          onChange={readOnly ? undefined : e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          readOnly={readOnly}
          placeholder="Enter your query for the pipeline..."
          rows={3}
          style={{
            width: '100%',
            background: 'var(--cr-charcoal-dark)',
            border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius-sm)',
            padding: '12px 50px 12px 14px',
            color: readOnly ? 'var(--cr-text-muted)' : 'var(--cr-text)',
            fontSize: '14px',
            resize: 'vertical',
            outline: 'none',
            boxSizing: 'border-box',
            fontFamily: 'inherit',
            lineHeight: '1.5',
          }}
        />
        {!readOnly && (
          <button
            onClick={handleSubmit}
            disabled={isRunning || !query.trim()}
            style={{
              position: 'absolute',
              right: '10px',
              bottom: '10px',
              background: isRunning || !query.trim() ? 'var(--cr-border)' : 'var(--cr-green-600)',
              border: 'none',
              borderRadius: 'var(--cr-radius-xs)',
              padding: '6px 8px',
              cursor: isRunning || !query.trim() ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background 200ms',
            }}
          >
            <Send style={{ width: 16, height: 16, color: 'var(--cr-text)' }} />
          </button>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '10px', flexWrap: 'wrap', gap: '8px' }}>
        {!readOnly && (
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {EXAMPLE_PROMPTS.map(prompt => (
              <button
                key={prompt}
                onClick={() => setQuery(prompt)}
                style={{
                  background: 'var(--cr-charcoal-dark)',
                  border: '1px solid var(--cr-border)',
                  borderRadius: 'var(--cr-radius-xs)',
                  padding: '3px 8px',
                  color: 'var(--cr-text-dim)',
                  fontSize: '11px',
                  cursor: 'pointer',
                  transition: 'color 150ms',
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-muted)'; }}
                onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-dim)'; }}
              >
                {prompt.length > 40 ? prompt.slice(0, 40) + '…' : prompt}
              </button>
            ))}
          </div>
        )}
        {estimatedCost != null && (
          <span
            style={{
              background: 'var(--cr-charcoal-dark)',
              color: 'var(--cr-gold-500)',
              fontSize: '11px',
              borderRadius: 'var(--cr-radius-xs)',
              padding: '3px 8px',
              fontWeight: 500,
              whiteSpace: 'nowrap',
            }}
          >
            ~${estimatedCost.toFixed(3)} est.
          </span>
        )}
        {!readOnly && (
          <span style={{ color: 'var(--cr-text-dim)', fontSize: '11px', whiteSpace: 'nowrap' }}>⌘↵ to run</span>
        )}
      </div>
    </div>
  );
}
