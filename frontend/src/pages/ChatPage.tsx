import { useState, useEffect, useRef, useCallback } from 'react';
import { ChevronDown, ChevronUp, Bot } from 'lucide-react';
import { api } from '../api/client';
import type { Specialist } from '../types';
import { useChat } from '../hooks/useChat';
import MessageBubble from '../components/chat/MessageBubble';
import ChatInput from '../components/chat/ChatInput';
import SpecialistHeader from '../components/chat/SpecialistHeader';

const EXAMPLE_PROMPTS: Record<string, string[]> = {
  'financial-analyst': [
    'Analyze the risk profile of a precious metals portfolio',
    'What are the key financial ratios for evaluating a lending company?',
  ],
  'research-assistant': [
    'Compare TILT lending regulations across northeastern states',
    'Summarize recent changes to UCC Article 9',
  ],
  'code-reviewer': [
    'Review this Python function for security vulnerabilities',
    'What are best practices for JWT token rotation?',
  ],
  'legal-quick': [
    'What are the Article I Section 10 implications for precious metals as legal tender?',
    'Outline the key TILA disclosure requirements for consumer lending',
  ],
};

const DEFAULT_PROMPTS = [
  'Help me understand this topic in detail',
  'What are the key considerations for this situation?',
];

export default function ChatPage() {
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [selected, setSelected] = useState<Specialist | null>(null);
  const [showSpecialistPanel, setShowSpecialistPanel] = useState(false);

  const { messages, isStreaming, error, sendMessage, stopStreaming } = useChat(
    selected?.id ?? null,
  );

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollPill, setShowScrollPill] = useState(false);

  useEffect(() => {
    api
      .request<{ specialists: Specialist[] }>('/specialists/')
      .then((data) => {
        setSpecialists(data.specialists);
        if (data.specialists.length > 0) setSelected(data.specialists[0]);
      })
      .catch(console.error);
  }, []);

  const isAtBottom = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < 100;
  }, []);

  useEffect(() => {
    if (isAtBottom()) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setShowScrollPill(false);
    } else if (messages.length > 0) {
      setShowScrollPill(true);
    }
  }, [messages, isAtBottom]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setShowScrollPill(false);
  };

  const handleScroll = () => {
    if (isAtBottom()) setShowScrollPill(false);
  };

  const examplePrompts = selected
    ? (EXAMPLE_PROMPTS[selected.id] ?? DEFAULT_PROMPTS)
    : DEFAULT_PROMPTS;

  return (
    <div className="flex" style={{ height: '100vh' }}>
      {/* Desktop specialist sidebar */}
      <div
        className="hidden md:block p-4 overflow-y-auto"
        style={{
          width: 260,
          borderRight: '1px solid var(--cr-border)',
          flexShrink: 0,
          background: 'var(--cr-charcoal)',
        }}
      >
        <h2
          style={{
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--cr-text-dim)',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            marginBottom: '12px',
          }}
        >
          Specialists
        </h2>
        {specialists.map((s) => (
          <button
            key={s.id}
            onClick={() => setSelected(s)}
            style={{
              width: '100%',
              textAlign: 'left',
              padding: '10px 12px',
              borderRadius: 'var(--cr-radius-sm)',
              marginBottom: '3px',
              border: 'none',
              background: selected?.id === s.id ? 'var(--cr-charcoal-deep)' : 'transparent',
              borderLeft: selected?.id === s.id ? '2px solid var(--cr-green-600)' : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 100ms',
            }}
            onMouseEnter={(e) => {
              if (selected?.id !== s.id) e.currentTarget.style.background = 'rgba(42,46,50,0.5)';
            }}
            onMouseLeave={(e) => {
              if (selected?.id !== s.id) e.currentTarget.style.background = 'transparent';
            }}
          >
            <div
              style={{
                fontSize: '13px',
                fontWeight: selected?.id === s.id ? 500 : 400,
                color: selected?.id === s.id ? 'var(--cr-green-400)' : 'var(--cr-text-muted)',
              }}
            >
              {s.name}
            </div>
            <div
              style={{
                fontSize: '11px',
                color: 'var(--cr-text-dim)',
                marginTop: '2px',
              }}
            >
              {s.description}
            </div>
          </button>
        ))}
        {specialists.length === 0 && (
          <div style={{ color: 'var(--cr-text-dim)', fontSize: '12px', padding: '8px' }}>
            Loading specialists...
          </div>
        )}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col" style={{ minWidth: 0, overflow: 'hidden' }}>
        {/* Mobile specialist selector */}
        <div className="md:hidden" style={{ borderBottom: '1px solid var(--cr-border)' }}>
          <button
            onClick={() => setShowSpecialistPanel(!showSpecialistPanel)}
            className="w-full flex items-center justify-between px-4 py-3"
            style={{ color: 'var(--cr-text)', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Bot style={{ width: 16, height: 16, color: 'var(--cr-green-400)' }} />
              <span style={{ fontSize: '14px', fontWeight: 500 }}>
                {selected?.name ?? 'Select Specialist'}
              </span>
            </div>
            {showSpecialistPanel ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
          {showSpecialistPanel && (
            <div style={{ padding: '0 8px 10px' }}>
              {specialists.map((s) => (
                <button
                  key={s.id}
                  onClick={() => { setSelected(s); setShowSpecialistPanel(false); }}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '10px 12px',
                    margin: '2px 0',
                    borderRadius: 'var(--cr-radius-sm)',
                    border: 'none',
                    background: selected?.id === s.id ? 'var(--cr-charcoal-deep)' : 'transparent',
                    borderLeft: selected?.id === s.id ? '2px solid var(--cr-green-600)' : '2px solid transparent',
                    cursor: 'pointer',
                    transition: 'all 100ms',
                  }}
                >
                  <div
                    style={{
                      fontSize: '13px',
                      fontWeight: selected?.id === s.id ? 500 : 400,
                      color: selected?.id === s.id ? 'var(--cr-green-400)' : 'var(--cr-text-muted)',
                    }}
                  >
                    {s.name}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '2px' }}>
                    {s.description}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {selected ? (
          <>
            <div className="hidden md:block">
              <SpecialistHeader specialist={selected} messageCount={messages.length} />
            </div>

            {/* Messages */}
            <div
              ref={scrollContainerRef}
              onScroll={handleScroll}
              className="flex-1 overflow-y-auto"
              style={{ padding: '16px 16px' }}
            >
              {messages.length === 0 ? (
                <div
                  style={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center',
                    gap: 12,
                  }}
                >
                  <div
                    style={{
                      width: 48,
                      height: 48,
                      borderRadius: '12px',
                      background: 'var(--cr-green-900)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '4px',
                    }}
                  >
                    <Bot style={{ width: 24, height: 24, color: 'var(--cr-green-400)' }} />
                  </div>
                  <div style={{ color: 'var(--cr-text)', fontSize: '18px', fontWeight: 600 }}>
                    {selected.name}
                  </div>
                  <div style={{ color: 'var(--cr-text-muted)', fontSize: '13px', maxWidth: 400 }}>
                    {selected.description}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginBottom: '12px' }}>
                    Powered by {selected.provider}/{selected.model}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 500 }}>
                    {examplePrompts.map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => sendMessage(prompt)}
                        style={{
                          background: 'var(--cr-charcoal)',
                          border: '1px solid var(--cr-border)',
                          borderRadius: '20px',
                          color: 'var(--cr-text-muted)',
                          fontSize: '12px',
                          padding: '6px 14px',
                          cursor: 'pointer',
                          transition: 'background 200ms, color 200ms',
                        }}
                        onMouseEnter={(e) => {
                          (e.currentTarget as HTMLButtonElement).style.background = 'var(--cr-charcoal-deep)';
                          (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-mist)';
                        }}
                        onMouseLeave={(e) => {
                          (e.currentTarget as HTMLButtonElement).style.background = 'var(--cr-charcoal)';
                          (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-muted)';
                        }}
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <MessageBubble
                    key={idx}
                    message={msg}
                    isStreaming={
                      isStreaming && idx === messages.length - 1 && msg.role === 'assistant'
                    }
                  />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {showScrollPill && (
              <div style={{ position: 'relative' }}>
                <button
                  onClick={scrollToBottom}
                  style={{
                    position: 'absolute',
                    bottom: 8,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'var(--cr-green-900)',
                    border: 'none',
                    borderRadius: 20,
                    color: 'var(--cr-text)',
                    fontSize: 12,
                    padding: '5px 14px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    zIndex: 10,
                  }}
                >
                  <ChevronDown size={14} />
                  New messages
                </button>
              </div>
            )}

            {error && (
              <div
                style={{
                  margin: '0 16px 8px',
                  padding: '8px 12px',
                  background: 'rgba(214, 69, 69, 0.08)',
                  border: '1px solid var(--cr-danger)',
                  borderRadius: 8,
                  color: 'var(--cr-danger)',
                  fontSize: 13,
                }}
              >
                {error}
              </div>
            )}

            <ChatInput
              onSend={sendMessage}
              onStop={stopStreaming}
              isStreaming={isStreaming}
              disabled={false}
              specialistName={selected.name}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p style={{ color: 'var(--cr-text-dim)' }}>Select a specialist to begin</p>
          </div>
        )}
      </div>
    </div>
  );
}

