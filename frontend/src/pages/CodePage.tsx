import { useState, useRef, useEffect, useCallback } from 'react';
import { Terminal, Send, Square, Trash2, ChevronDown } from 'lucide-react';
import { api } from '../api/client';
import type { ChatMessage } from '../types';

const CODE_SYSTEM_ID = 'code-reviewer'; // Uses Code Reviewer specialist

/**
 * CodePage — Terminal-style code assistant interface.
 *
 * Dark-themed, monospace, output rendered as streaming text blocks.
 * Connected to the Code Reviewer specialist for architecture, code review,
 * debugging, and generation tasks.
 */
export default function CodePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const stoppedRef = useRef(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  // Focus input on mount
  useEffect(() => { inputRef.current?.focus(); }, []);

  const handleSend = async () => {
    const content = input.trim();
    if (!content || isStreaming) return;

    setInput('');
    setError(null);
    stoppedRef.current = false;

    const userMessage: ChatMessage = { role: 'user', content };
    const history = messages.map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev, userMessage, { role: 'assistant', content: '' }]);
    setIsStreaming(true);

    try {
      await api.streamChat(
        CODE_SYSTEM_ID,
        content,
        history,
        (chunk) => {
          if (stoppedRef.current) return;
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx < 0 || updated[lastIdx].role !== 'assistant') return prev;
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: updated[lastIdx].content + chunk.content,
              ...(chunk.is_final ? {
                tokens: { input: chunk.input_tokens, output: chunk.output_tokens },
                cost_usd: chunk.cost_usd,
              } : {}),
            };
            return updated;
          });
        },
      );
    } catch (err) {
      if (!stoppedRef.current) {
        setError(err instanceof Error ? err.message : 'Stream failed');
      }
    } finally {
      if (!stoppedRef.current) setIsStreaming(false);
    }
  };

  const handleStop = () => { stoppedRef.current = true; setIsStreaming(false); };

  const handleClear = () => {
    setMessages([]);
    setError(null);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#0D1117',
      color: '#C9D1D9',
      fontFamily: "'JetBrains Mono', 'Fira Code', 'SF Mono', 'Cascadia Code', Consolas, monospace",
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 20px',
        borderBottom: '1px solid #21262D',
        background: '#161B22',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Terminal style={{ width: 18, height: 18, color: '#58A6FF' }} />
          <span style={{ fontWeight: 600, fontSize: 15, color: '#E6EDF3' }}>
            Calculus Code
          </span>
          <span style={{ fontSize: 11, color: '#484F58', marginLeft: 4 }}>
            v1.0
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {messages.length > 0 && (
            <button
              onClick={handleClear}
              title="Clear session"
              style={{
                background: 'none',
                border: '1px solid #30363D',
                borderRadius: 6,
                padding: '5px 10px',
                color: '#8B949E',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                fontSize: 12,
              }}
            >
              <Trash2 style={{ width: 13, height: 13 }} />
              Clear
            </button>
          )}
          <div style={{
            fontSize: 11,
            color: '#484F58',
            padding: '4px 8px',
            border: '1px solid #21262D',
            borderRadius: 4,
          }}>
            gemini-2.5-pro
          </div>
        </div>
      </div>

      {/* Messages / Terminal Output */}
      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px 20px',
        }}
      >
        {messages.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 16 }}>
            <Terminal style={{ width: 48, height: 48, color: '#21262D' }} />
            <div style={{ color: '#484F58', fontSize: 14, textAlign: 'center', maxWidth: 500, lineHeight: 1.6 }}>
              <div style={{ color: '#58A6FF', fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Calculus Code</div>
              Code review, architecture design, debugging, and generation.
              <br />
              Type a request below or try:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxWidth: 600, width: '100%' }}>
              {[
                'Review this Python function for security vulnerabilities',
                'Design a database schema for multi-tenant loan servicing',
                'Write a FastAPI endpoint for covenant compliance checking',
                'Explain the trade-offs between PostgreSQL and MongoDB for financial data',
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => { setInput(prompt); inputRef.current?.focus(); }}
                  style={{
                    background: '#161B22',
                    border: '1px solid #21262D',
                    borderRadius: 6,
                    padding: '10px 14px',
                    color: '#8B949E',
                    fontSize: 13,
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 120ms',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#58A6FF'; e.currentTarget.style.color = '#C9D1D9'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#21262D'; e.currentTarget.style.color = '#8B949E'; }}
                >
                  <span style={{ color: '#58A6FF', marginRight: 8 }}>$</span>
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} style={{ marginBottom: 16 }}>
              {msg.role === 'user' ? (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <span style={{ color: '#3FB950', fontWeight: 600, fontSize: 12 }}>you</span>
                    <span style={{ color: '#30363D' }}>~</span>
                    <ChevronDown style={{ width: 10, height: 10, color: '#30363D', transform: 'rotate(-90deg)' }} />
                  </div>
                  <div style={{ color: '#E6EDF3', fontSize: 13, paddingLeft: 4, whiteSpace: 'pre-wrap' }}>
                    {msg.content}
                  </div>
                </div>
              ) : (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <span style={{ color: '#58A6FF', fontWeight: 600, fontSize: 12 }}>calculus</span>
                    <span style={{ color: '#30363D' }}>~</span>
                    {isStreaming && idx === messages.length - 1 && (
                      <span style={{ color: '#F0883E', fontSize: 11 }}>streaming...</span>
                    )}
                    {msg.cost_usd !== undefined && (
                      <span style={{ color: '#484F58', fontSize: 11, marginLeft: 'auto' }}>
                        ${msg.cost_usd.toFixed(4)} | {((msg.tokens?.input ?? 0) + (msg.tokens?.output ?? 0)).toLocaleString()} tok
                      </span>
                    )}
                  </div>
                  <div style={{
                    color: '#C9D1D9',
                    fontSize: 13,
                    paddingLeft: 4,
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                  }}>
                    {msg.content}
                    {isStreaming && idx === messages.length - 1 && (
                      <span style={{ color: '#58A6FF', animation: 'blink 1s infinite' }}>|</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Error */}
      {error && (
        <div style={{ margin: '0 20px 8px', padding: '8px 12px', background: '#3D1F1F', border: '1px solid #6E3630', borderRadius: 6, color: '#F85149', fontSize: 13 }}>
          {error}
        </div>
      )}

      {/* Input */}
      <div style={{
        padding: '12px 20px 16px',
        borderTop: '1px solid #21262D',
        background: '#161B22',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 8,
          background: '#0D1117',
          border: '1px solid #30363D',
          borderRadius: 8,
          padding: '10px 12px',
        }}>
          <span style={{ color: '#3FB950', fontSize: 14, fontWeight: 600, userSelect: 'none', paddingBottom: 2 }}>$</span>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command..."
            rows={1}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#E6EDF3',
              fontSize: 14,
              fontFamily: 'inherit',
              resize: 'none',
              lineHeight: 1.5,
              maxHeight: 120,
              overflow: 'auto',
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = Math.min(target.scrollHeight, 120) + 'px';
            }}
          />
          {isStreaming ? (
            <button onClick={handleStop} style={{ background: '#F85149', border: 'none', borderRadius: 6, padding: '6px 8px', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
              <Square style={{ width: 14, height: 14, color: '#fff' }} />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              style={{
                background: input.trim() ? '#238636' : '#21262D',
                border: 'none',
                borderRadius: 6,
                padding: '6px 8px',
                cursor: input.trim() ? 'pointer' : 'default',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              <Send style={{ width: 14, height: 14, color: input.trim() ? '#fff' : '#484F58' }} />
            </button>
          )}
        </div>
        <div style={{ fontSize: 11, color: '#30363D', marginTop: 6, textAlign: 'center' }}>
          Enter to send &middot; Shift+Enter for new line
        </div>
      </div>

      {/* Blink animation */}
      <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
