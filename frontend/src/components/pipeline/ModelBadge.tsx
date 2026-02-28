const MODEL_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  'gpt-4o':              { bg: '#1a3a2a', text: '#4ade80', label: 'GPT-4o' },
  'gpt-4.5':             { bg: '#1a3a2a', text: '#4ade80', label: 'GPT-4.5' },
  'gpt-5':               { bg: '#1a3a2a', text: '#4ade80', label: 'GPT-5' },
  'grok-3-mini-beta':    { bg: '#3a2a1a', text: '#f59e0b', label: 'Grok' },
  'grok-4':              { bg: '#3a2a1a', text: '#f59e0b', label: 'Grok 4' },
  'grok-4-fast':         { bg: '#3a2a1a', text: '#f59e0b', label: 'Grok 4F' },
  'gemini-2.5-flash':    { bg: '#1a2a3a', text: '#60a5fa', label: 'Gemini' },
  'gemini-2.5-pro':      { bg: '#1a2a3a', text: '#60a5fa', label: 'Gemini Pro' },
  'gemini-3-pro':        { bg: '#1a2a3a', text: '#60a5fa', label: 'Gemini 3' },
  'claude-4-opus':       { bg: '#2a1a3a', text: '#c084fc', label: 'Claude' },
  'claude-sonnet-4.5':   { bg: '#2a1a3a', text: '#c084fc', label: 'Sonnet' },
};

function resolveModel(model: string): { bg: string; text: string; label: string } {
  if (MODEL_COLORS[model]) return MODEL_COLORS[model];
  const stripped = model.replace(/^(xai\/|gemini\/|anthropic\/|openai\/)/, '');
  if (MODEL_COLORS[stripped]) return MODEL_COLORS[stripped];
  const lower = model.toLowerCase();
  if (lower.includes('gpt') || lower.includes('openai'))   return { bg: '#1a3a2a', text: '#4ade80', label: 'GPT' };
  if (lower.includes('grok') || lower.includes('xai'))     return { bg: '#3a2a1a', text: '#f59e0b', label: 'Grok' };
  if (lower.includes('gemini') || lower.includes('google')) return { bg: '#1a2a3a', text: '#60a5fa', label: 'Gemini' };
  if (lower.includes('claude') || lower.includes('anthro')) return { bg: '#2a1a3a', text: '#c084fc', label: 'Claude' };
  return { bg: '#2a2a2a', text: '#999', label: model.slice(0, 8) };
}

interface ModelBadgeProps {
  model: string;
}

export default function ModelBadge({ model }: ModelBadgeProps) {
  const { bg, text, label } = resolveModel(model);
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        borderRadius: '10px',
        background: bg,
        color: text,
        fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.02em',
        whiteSpace: 'nowrap',
        lineHeight: '18px',
      }}
    >
      {label}
    </span>
  );
}

