import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Crown, Sparkles, Zap } from 'lucide-react';
import type { LLMProvider } from '../../types';

// Provider accent colors
const PROVIDER_COLORS: Record<string, string> = {
  openai: '#3E9B5F',
  anthropic: '#F2A41F',
  google: '#4285F4',
  grok: '#D64545',
  deepseek: '#7C8CF5',
  mistral: '#E8853D',
  groq: '#E8853D',  // orange (Groq brand)
};

// Tier config
const TIER_CONFIG: Record<string, { icon: typeof Crown; color: string; label: string }> = {
  top: { icon: Crown, color: '#F2A41F', label: 'TOP' },
  mid: { icon: Sparkles, color: 'var(--cr-text-dim)', label: 'MID' },
  budget: { icon: Zap, color: 'var(--cr-green-600)', label: '💰' },
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

// ── Grid Mode ───────────────────────────────────────────────────

function GridSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelect,
}: Omit<ModelSelectorProps, 'mode'>) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '12px',
        maxWidth: '960px',
        width: '100%',
      }}
    >
      {providers.map((prov) => {
        const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
        return (
          <div
            key={prov.id}
            style={{
              background: 'var(--cr-charcoal)',
              borderRadius: 'var(--cr-radius)',
              border: '1px solid var(--cr-border)',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
            }}
          >
            {/* Provider header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: accent,
                }}
              />
              <span
                style={{
                  fontSize: '13px',
                  fontWeight: 600,
                  color: 'var(--cr-mist)',
                  letterSpacing: '0.02em',
                }}
              >
                {prov.name}
              </span>
            </div>

            {/* Models */}
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
                    flexDirection: 'column',
                    gap: '4px',
                    padding: '10px 12px',
                    borderRadius: 'var(--cr-radius-sm)',
                    border: isSelected ? `2px solid ${accent}` : '1px solid var(--cr-border)',
                    background: isSelected ? `${accent}15` : 'var(--cr-charcoal-dark)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    width: '100%',
                    transition: 'all 150ms',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TierIcon style={{ width: '14px', height: '14px', color: tier.color, flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div
                        style={{
                          fontSize: '13px',
                          fontWeight: 500,
                          color: isSelected ? '#FFFFFF' : '#D0D8E0',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {m.name}
                      </div>
                    </div>
                    {m.context && (
                      <span
                        style={{
                          fontSize: '10px',
                          fontWeight: 500,
                          color: 'var(--cr-text-muted)',
                          background: 'var(--cr-charcoal-deep)',
                          padding: '1px 5px',
                          borderRadius: 'var(--cr-radius-xs)',
                          flexShrink: 0,
                        }}
                      >
                        {m.context}
                      </span>
                    )}
                  </div>
                  {m.description && (
                    <div
                      style={{
                        fontSize: '11px',
                        color: 'var(--cr-text-dim)',
                        lineHeight: '1.3',
                        overflow: 'hidden',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {m.description}
                    </div>
                  )}
                  <div style={{ fontSize: '11px', color: 'var(--cr-text-dim)' }}>
                    {formatPrice(m.input_price, m.output_price)}/1M
                  </div>
                </button>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

// ── Compact Mode ────────────────────────────────────────────────

function CompactSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelect,
}: Omit<ModelSelectorProps, 'mode'>) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isOpen]);

  // Find selected model info
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
            minWidth: '320px',
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
                      <TierIcon style={{ width: '13px', height: '13px', color: tier.color, flexShrink: 0 }} />
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
                        {m.description && (
                          <div
                            style={{
                              fontSize: '10px',
                              color: 'var(--cr-text-dim)',
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              marginTop: '1px',
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
