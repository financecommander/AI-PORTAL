import { useState, useEffect, useRef, useCallback } from 'react';
import { ChevronDown } from 'lucide-react';
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

  // Auto-scroll when messages change if user is near bottom
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
      {/* Specialist selector */}
      <div
        className="p-4 overflow-y-auto"
        style={{
          width: 256,
          borderRight: '1px solid #2A3A5C',
          flexShrink: 0,
        }}
      >
        <h2 className="text-sm font-semibold text-white mb-3">Specialists</h2>
        {specialists.map((s) => (
          <button
            key={s.id}
            onClick={() => setSelected(s)}
            className="w-full text-left px-3 py-2.5 rounded-lg text-sm mb-1 transition-all"
            style={{
              background: selected?.id === s.id ? 'var(--navy-light)' : 'transparent',
              color: selected?.id === s.id ? '#FFFFFF' : '#8899AA',
            }}
          >
            <div className="font-medium">{s.name}</div>
            <div className="text-xs mt-0.5 opacity-60">
              {s.provider} / {s.model}
            </div>
          </button>
        ))}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col" style={{ minWidth: 0, overflow: 'hidden' }}>
        {selected ? (
          <>
            <SpecialistHeader specialist={selected} messageCount={messages.length} />

            {/* Messages */}
            <div
              ref={scrollContainerRef}
              onScroll={handleScroll}
              className="flex-1 overflow-y-auto"
              style={{ padding: '16px 24px' }}
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
                  <div style={{ color: '#FFFFFF', fontSize: 20, fontWeight: 600 }}>
                    {selected.name}
                  </div>
                  <div style={{ color: '#8899AA', fontSize: 14, marginBottom: 8 }}>
                    Start a conversation with {selected.name}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 480 }}>
                    {examplePrompts.map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => sendMessage(prompt)}
                        style={{
                          background: 'var(--navy-light)',
                          border: '1px solid #2A3A5C',
                          borderRadius: 20,
                          color: '#8899AA',
                          fontSize: 13,
                          padding: '6px 14px',
                          cursor: 'pointer',
                          transition: 'background 200ms',
                        }}
                        onMouseEnter={(e) =>
                          ((e.currentTarget as HTMLButtonElement).style.background = '#2A3A5C')
                        }
                        onMouseLeave={(e) =>
                          ((e.currentTarget as HTMLButtonElement).style.background =
                            'var(--navy-light)')
                        }
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

            {/* New messages scroll pill */}
            {showScrollPill && (
              <div style={{ position: 'relative' }}>
                <button
                  onClick={scrollToBottom}
                  style={{
                    position: 'absolute',
                    bottom: 8,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'var(--blue)',
                    border: 'none',
                    borderRadius: 20,
                    color: '#fff',
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

            {/* Error */}
            {error && (
              <div
                style={{
                  margin: '0 24px 8px',
                  padding: '8px 12px',
                  background: '#3A1A1A',
                  border: '1px solid var(--red)',
                  borderRadius: 8,
                  color: '#FF8888',
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
            <p style={{ color: '#667788' }}>Select a specialist to begin</p>
          </div>
        )}
      </div>
    </div>
  );
}
