import { useState, useRef, useEffect } from 'react';
import { ChevronDown, ChevronRight, Crown, Sparkles, Zap } from 'lucide-react';
import type { LLMProvider } from '../../types';

// Provider accent colors
const PROVIDER_COLORS: Record<string, string> = {
  openai: '#3E9B5F',
  anthropic: '#F2A41F',
  google: '#4285F4',
  grok: '#D64545',
  deepseek: '#7C8CF5',
  mistral: '#E8853D',
  groq: '#E8853D',
};

const TIER_CONFIG: Record<string, { icon: typeof Crown; color: string }> = {
  top: { icon: Crown, color: '#F2A41F' },
  mid: { icon: Sparkles, color: 'var(--cr-text-dim)' },
  budget: { icon: Zap, color: 'var(--cr-green-600)' },
};

interface ModelSelectorProps {
  providers: LLMProvider[];
  selectedProvider: string | null;
  selectedModel: string | null;
  onSelect: (provider: string, model: string) => void;
  mode: 'grid' | 'compact';
}

function formatPrice(input?: number, output?: number): string {
  if (input == null || output == null) return '';
  if (input < 1) return `$${input.toFixed(2)}/$${output.toFixed(2)}`;
  return `$${input.toFixed(2)}/$${output.toFixed(0)}`;
}

// ── Grid Mode — Collapsible accordions per provider ─────────────

function GridSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelect,
}: Omit<ModelSelectorProps, 'mode'>) {
  // Track which providers are expanded; default first provider open
  const [expanded, setExpanded] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    providers.forEach((p, i) => {
      init[p.id] = i === 0; // first provider open by default
    });
    return init;
  });

  // If selected provider changes, expand it
  useEffect(() => {
    if (selectedProvider) {
      setExpanded((prev) => ({ ...prev, [selectedProvider]: true }));
    }
  }, [selectedProvider]);

  const toggleProvider = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        maxWidth: '700px',
        width: '100%',
      }}
    >
      {providers.map((prov) => {
        const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
        const isExpanded = expanded[prov.id] ?? false;
        const hasSelected = selectedProvider === prov.id;

        return (
          <div
            key={prov.id}
            style={{
              background: 'var(--cr-charcoal)',
              borderRadius: 'var(--cr-radius)',
              border: hasSelected ? `1px solid ${accent}40` : '1px solid var(--cr-border)',
              overflow: 'hidden',
              transition: 'border-color 150ms',
            }}
          >
            {/* Provider header — click to expand/collapse */}
            <button
              onClick={() => toggleProvider(prov.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                width: '100%',
                padding: '12px 16px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                transition: 'background 100ms',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--cr-charcoal-deep)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
              }}
            >
              <div
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: accent,
                  flexShrink: 0,
                }}
              />
              <span
                style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  color: 'var(--cr-text)',
                  flex: 1,
                  textAlign: 'left',
                  letterSpacing: '0.01em',
                }}
              >
                {prov.name}
              </span>
              <span
                style={{
                  fontSize: '11px',
                  color: 'var(--cr-text-dim)',
                  marginRight: '4px',
                }}
              >
                {prov.models.length} model{prov.models.length !== 1 ? 's' : ''}
              </span>
              {isExpanded ? (
                <ChevronDown
                  style={{ width: 16, height: 16, color: 'var(--cr-text-muted)', transition: 'transform 150ms' }}
                />
              ) : (
                <ChevronRight
                  style={{ width: 16, height: 16, color: 'var(--cr-text-muted)', transition: 'transform 150ms' }}
                />
              )}
            </button>

            {/* Models list — collapsible */}
            {isExpanded && (
              <div style={{ padding: '0 8px 8px' }}>
                {prov.models.map((m) => {
                  const isSelected = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button
                      key={m.id}
                      onClick={() => onSelect(prov.id, m.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        width: '100%',
                        padding: '10px 12px',
                        margin: '2px 0',
                        borderRadius: 'var(--cr-radius-sm)',
                        border: isSelected ? `1px solid ${accent}` : '1px solid transparent',
                        background: isSelected ? `${accent}15` : 'transparent',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 100ms',
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) e.currentTarget.style.background = 'var(--cr-charcoal-deep)';
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) e.currentTarget.style.background = 'transparent';
                      }}
                    >
                      <TierIcon style={{ width: 14, height: 14, color: tier.color, flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div
                          style={{
                            fontSize: '13px',
                            fontWeight: isSelected ? 600 : 400,
                            color: isSelected ? 'var(--cr-text)' : 'var(--cr-mist)',
                          }}
                        >
                          {m.name}
                        </div>
                        {m.description && (
                          <div
                            style={{
                              fontSize: '11px',
                              color: 'var(--cr-text-dim)',
                              marginTop: '1px',
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                            }}
                          >
                            {m.description}
                          </div>
                        )}
                      </div>
                      {m.context && (
                        <span
                          style={{
                            fontSize: '10px',
                            color: 'var(--cr-text-dim)',
                            background: 'var(--cr-charcoal-deep)',
                            padding: '2px 6px',
                            borderRadius: 'var(--cr-radius-xs)',
                            flexShrink: 0,
                          }}
                        >
                          {m.context}
                        </span>
                      )}
                      <span style={{ fontSize: '11px', color: 'var(--cr-text-dim)', flexShrink: 0 }}>
                        {formatPrice(m.input_price, m.output_price)}/1M
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Compact Mode (dropdown in header bar during chat) ────────────

function CompactSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelect,
}: Omit<ModelSelectorProps, 'mode'>) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isOpen]);

  let selectedModelName = 'Select model';
  let selectedAccent = 'var(--cr-green-600)';
  let selectedContext = '';
  for (const prov of providers) {
    for (const m of prov.models) {
      if (prov.id === selectedProvider && m.id === selectedModel) {
        selectedModelName = m.name;
        selectedAccent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
        selectedContext = m.context || '';
      }
    }
  }

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 14px',
          borderRadius: 'var(--cr-radius-sm)',
          border: '1px solid var(--cr-border)',
          background: 'var(--cr-charcoal)',
          cursor: 'pointer',
          transition: 'all 150ms',
        }}
      >
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: selectedAccent,
          }}
        />
        <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--cr-text)' }}>
          {selectedModelName}
        </span>
        {selectedContext && (
          <span style={{ fontSize: '10px', color: 'var(--cr-text-dim)' }}>
            {selectedContext}
          </span>
        )}
        <ChevronDown
          style={{
            width: '14px',
            height: '14px',
            color: 'var(--cr-text-muted)',
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0)',
            transition: 'transform 150ms',
          }}
        />
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            minWidth: '340px',
            maxHeight: '420px',
            overflowY: 'auto',
            background: 'var(--cr-charcoal-deep)',
            border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius)',
            padding: '8px',
            zIndex: 50,
            boxShadow: '0 12px 40px rgba(0,0,0,0.5)',
          }}
        >
          {providers.map((prov) => {
            const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
            return (
              <div key={prov.id}>
                <div
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    color: 'var(--cr-text-dim)',
                    padding: '8px 10px 4px',
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                  }}
                >
                  {prov.name}
                </div>
                {prov.models.map((m) => {
                  const isActive = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button
                      key={m.id}
                      onClick={() => {
                        onSelect(prov.id, m.id);
                        setIsOpen(false);
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        width: '100%',
                        padding: '8px 10px',
                        borderRadius: 'var(--cr-radius-xs)',
                        border: 'none',
                        background: isActive ? `${accent}15` : 'transparent',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'background 100ms',
                      }}
                      onMouseEnter={(e) => {
                        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'var(--cr-charcoal)';
                      }}
                      onMouseLeave={(e) => {
                        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'transparent';
                      }}
                    >
                      <TierIcon style={{ width: 13, height: 13, color: tier.color, flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <span
                          style={{
                            fontSize: '13px',
                            fontWeight: isActive ? 500 : 400,
                            color: isActive ? 'var(--cr-text)' : 'var(--cr-mist)',
                          }}
                        >
                          {m.name}
                        </span>
                      </div>
                      {m.context && (
                        <span
                          style={{
                            fontSize: '10px',
                            color: 'var(--cr-text-dim)',
                            background: 'var(--cr-charcoal-deep)',
                            padding: '1px 4px',
                            borderRadius: 'var(--cr-radius-xs)',
                            flexShrink: 0,
                          }}
                        >
                          {m.context}
                        </span>
                      )}
                      <span style={{ fontSize: '11px', color: 'var(--cr-text-dim)', flexShrink: 0 }}>
                        {formatPrice(m.input_price, m.output_price)}
                      </span>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── Export ───────────────────────────────────────────────────────

export default function ModelSelector(props: ModelSelectorProps) {
  return props.mode === 'grid' ? (
    <GridSelector {...props} />
  ) : (
    <CompactSelector {...props} />
  );
}

