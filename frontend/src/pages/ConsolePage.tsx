import { useState, useEffect, useRef, useCallback } from 'react';
import { Terminal, Server, WifiOff, Send, Loader2, AlertTriangle, ChevronRight, RefreshCw } from 'lucide-react';
import { api } from '../api/client';
import type { ConsoleHost, ConsoleEntry, CommandPlan, ConsoleEvent } from '../types';

let _entryId = 0;
function nextId() { return `ce-${++_entryId}`; }

export default function ConsolePage() {
  const [hosts, setHosts] = useState<(ConsoleHost & { status?: string })[]>([]);
  const [entries, setEntries] = useState<ConsoleEntry[]>([]);
  const [input, setInput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [hostsLoading, setHostsLoading] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Load hosts on mount
  useEffect(() => {
    loadHosts();
  }, []);

  // Auto-scroll on new output
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [entries]);

  const loadHosts = async () => {
    setHostsLoading(true);
    try {
      const data = await api.getConsoleHosts();
      setHosts(data.hosts.map((h) => ({ ...h, status: 'unknown' })));
    } catch (err) {
      console.error('Failed to load hosts:', err);
    } finally {
      setHostsLoading(false);
    }
  };

  const testHost = async (alias: string) => {
    setHosts((prev) => prev.map((h) => h.alias === alias ? { ...h, status: 'testing' } : h));
    try {
      const result = await api.testConsoleHost(alias);
      setHosts((prev) => prev.map((h) => h.alias === alias ? { ...h, status: result.status } : h));
    } catch {
      setHosts((prev) => prev.map((h) => h.alias === alias ? { ...h, status: 'error' } : h));
    }
  };

  const testAllHosts = async () => {
    for (const h of hosts) {
      testHost(h.alias);
    }
  };

  const handleSubmit = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isRunning) return;

    setInput('');
    setIsRunning(true);

    const entryId = nextId();
    const entry: ConsoleEntry = {
      id: entryId,
      input: trimmed,
      output: '',
      stderr: '',
      isRunning: true,
      timestamp: new Date(),
    };
    setEntries((prev) => [...prev, entry]);

    const updateEntry = (updates: Partial<ConsoleEntry>) => {
      setEntries((prev) =>
        prev.map((e) => e.id === entryId ? { ...e, ...updates } : e)
      );
    };

    try {
      await api.streamConsoleCommand(trimmed, (event: ConsoleEvent) => {
        switch (event.type) {
          case 'plan':
            updateEntry({
              plan: {
                host: event.data.host ?? null,
                command: event.data.command ?? null,
                explanation: event.data.explanation ?? null,
                risk: event.data.risk ?? 'low',
                error: event.data.error ?? null,
              } as CommandPlan,
            });
            break;
          case 'executing':
            // Command is now running
            break;
          case 'stdout':
            setEntries((prev) =>
              prev.map((e) =>
                e.id === entryId
                  ? { ...e, output: e.output + (event.data.text ?? '') }
                  : e
              )
            );
            break;
          case 'stderr':
            setEntries((prev) =>
              prev.map((e) =>
                e.id === entryId
                  ? { ...e, stderr: e.stderr + (event.data.text ?? '') }
                  : e
              )
            );
            break;
          case 'status':
            updateEntry({
              status: event.data.text ?? undefined,
              isRunning: false,
            });
            break;
          case 'error':
            updateEntry({
              error: event.data.message ?? 'Unknown error',
              isRunning: false,
            });
            break;
        }
      });
    } catch (err) {
      updateEntry({
        error: err instanceof Error ? err.message : 'Command failed',
        isRunning: false,
      });
    } finally {
      setIsRunning(false);
      updateEntry({ isRunning: false });
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [input, isRunning]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const statusDot = (status?: string) => {
    const colors: Record<string, string> = {
      connected: 'var(--cr-green-600)',
      testing: 'var(--cr-amber)',
      failed: 'var(--cr-danger)',
      error: 'var(--cr-danger)',
      unknown: 'var(--cr-text-dim)',
    };
    return colors[status ?? 'unknown'] ?? 'var(--cr-text-dim)';
  };

  const riskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'var(--cr-danger)';
      case 'medium': return 'var(--cr-amber)';
      default: return 'var(--cr-green-600)';
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#0d1117' }}>
      {/* Header */}
      <div style={{
        padding: '16px 24px',
        borderBottom: '1px solid #21262d',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#161b22',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #238636 0%, #1a7f37 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Terminal size={20} color="#fff" />
          </div>
          <div>
            <div style={{ color: '#e6edf3', fontSize: 16, fontWeight: 600, fontFamily: "'Space Grotesk', sans-serif" }}>
              Console Intelligence
            </div>
            <div style={{ color: '#7d8590', fontSize: 11 }}>
              Natural language → SSH execution
            </div>
          </div>
        </div>

        {/* Host status pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {hostsLoading ? (
            <div style={{ color: '#7d8590', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Loader2 size={14} className="animate-spin" /> Loading hosts...
            </div>
          ) : hosts.length === 0 ? (
            <div style={{ color: '#7d8590', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
              <WifiOff size={14} /> No hosts configured
            </div>
          ) : (
            <>
              {hosts.map((h) => (
                <button
                  key={h.alias}
                  onClick={() => testHost(h.alias)}
                  title={`${h.alias}: ${h.description || h.hostname} (${h.status ?? 'unknown'})\nClick to test`}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    padding: '4px 10px', borderRadius: 20,
                    background: '#21262d', border: '1px solid #30363d',
                    color: '#e6edf3', fontSize: 12, cursor: 'pointer',
                    transition: 'border-color 150ms',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#58a6ff'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#30363d'; }}
                >
                  <div style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: statusDot(h.status),
                    transition: 'background 300ms',
                  }} />
                  <Server size={12} />
                  {h.alias}
                </button>
              ))}
              <button
                onClick={testAllHosts}
                title="Test all connections"
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  width: 28, height: 28, borderRadius: 6,
                  background: 'transparent', border: '1px solid #30363d',
                  color: '#7d8590', cursor: 'pointer',
                }}
              >
                <RefreshCw size={14} />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Terminal output area */}
      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px 24px',
          fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
          fontSize: 13,
          lineHeight: 1.7,
        }}
      >
        {entries.length === 0 ? (
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16 }}>
            <Terminal size={48} color="#30363d" />
            <div style={{ color: '#7d8590', fontSize: 15, fontWeight: 500, fontFamily: "'Space Grotesk', sans-serif" }}>
              Console Intelligence
            </div>
            <div style={{ color: '#484f58', fontSize: 13, textAlign: 'center', maxWidth: 500, lineHeight: 1.8 }}>
              Type natural language commands and they'll be translated to SSH
              commands and executed on your configured hosts.
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 600, marginTop: 8 }}>
              {[
                'check disk space on mainframe',
                'restart Ollama on swarm-gpu',
                'show running docker containers on triton',
                'git pull on all hosts',
                'tail last 50 lines of syslog on mainframe',
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => { setInput(prompt); setTimeout(() => inputRef.current?.focus(), 50); }}
                  style={{
                    background: '#21262d', border: '1px solid #30363d',
                    borderRadius: 20, color: '#7d8590', fontSize: 12,
                    padding: '6px 14px', cursor: 'pointer', transition: 'all 150ms',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#238636'; e.currentTarget.style.color = '#e6edf3'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#30363d'; e.currentTarget.style.color = '#7d8590'; }}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          entries.map((entry) => (
            <div key={entry.id} style={{ marginBottom: 24 }}>
              {/* User input */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 8 }}>
                <ChevronRight size={16} color="#238636" style={{ marginTop: 2, flexShrink: 0 }} />
                <span style={{ color: '#e6edf3', fontWeight: 500 }}>{entry.input}</span>
              </div>

              {/* Command plan */}
              {entry.plan && (
                <div style={{
                  margin: '8px 0 8px 24px',
                  padding: '10px 14px',
                  background: '#161b22',
                  border: '1px solid #30363d',
                  borderRadius: 8,
                  fontSize: 12,
                }}>
                  {entry.plan.error ? (
                    <div style={{ color: 'var(--cr-danger)', display: 'flex', alignItems: 'center', gap: 6 }}>
                      <AlertTriangle size={14} /> {entry.plan.error}
                    </div>
                  ) : (
                    <>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                        <span style={{ color: '#7d8590' }}>Host:</span>
                        <span style={{
                          color: '#58a6ff', background: '#0d1d31', padding: '1px 8px',
                          borderRadius: 4, fontSize: 11,
                        }}>
                          {entry.plan.host}
                        </span>
                        <span style={{ color: '#7d8590' }}>Risk:</span>
                        <span style={{
                          color: riskColor(entry.plan.risk),
                          background: entry.plan.risk === 'high' ? '#3d1418' : entry.plan.risk === 'medium' ? '#3d2e12' : '#12261e',
                          padding: '1px 8px', borderRadius: 4, fontSize: 11,
                        }}>
                          {entry.plan.risk}
                        </span>
                      </div>
                      <div style={{ color: '#7d8590', marginBottom: 4 }}>{entry.plan.explanation}</div>
                      <div style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        color: '#f0883e', background: '#1c1105',
                        padding: '6px 10px', borderRadius: 4,
                        fontSize: 12, overflowX: 'auto',
                      }}>
                        $ {entry.plan.command}
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* stdout */}
              {entry.output && (
                <pre style={{
                  margin: '0 0 0 24px',
                  color: '#adbac7',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontSize: 12,
                  lineHeight: 1.6,
                }}>
                  {entry.output}
                </pre>
              )}

              {/* stderr */}
              {entry.stderr && (
                <pre style={{
                  margin: '4px 0 0 24px',
                  color: '#f47067',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontSize: 12,
                  lineHeight: 1.6,
                }}>
                  {entry.stderr}
                </pre>
              )}

              {/* Error */}
              {entry.error && (
                <div style={{
                  margin: '4px 0 0 24px',
                  color: '#f47067',
                  display: 'flex', alignItems: 'center', gap: 6,
                  fontSize: 12,
                }}>
                  <AlertTriangle size={14} /> {entry.error}
                </div>
              )}

              {/* Status / spinner */}
              {entry.isRunning ? (
                <div style={{ margin: '8px 0 0 24px', display: 'flex', alignItems: 'center', gap: 6, color: '#7d8590', fontSize: 12 }}>
                  <Loader2 size={14} className="animate-spin" /> Executing...
                </div>
              ) : entry.status !== undefined && entry.status !== 'blocked' && (
                <div style={{
                  margin: '8px 0 0 24px',
                  fontSize: 11,
                  color: entry.status === '0' ? '#3fb950' : '#f47067',
                }}>
                  exit {entry.status}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Input area */}
      <div style={{
        padding: '12px 24px 16px',
        borderTop: '1px solid #21262d',
        background: '#161b22',
      }}>
        <div style={{
          display: 'flex', alignItems: 'flex-end', gap: 8,
          background: '#0d1117',
          border: '1px solid #30363d',
          borderRadius: 12,
          padding: '8px 12px',
          transition: 'border-color 150ms',
        }}>
          <ChevronRight size={18} color="#238636" style={{ flexShrink: 0, marginBottom: 4 }} />
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='Type a command in plain English... (e.g. "check disk space on mainframe")'
            rows={1}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#e6edf3',
              fontSize: 14,
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              resize: 'none',
              lineHeight: 1.6,
            }}
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isRunning}
            style={{
              width: 36, height: 36, borderRadius: 8,
              background: input.trim() && !isRunning ? '#238636' : '#21262d',
              border: 'none',
              color: input.trim() && !isRunning ? '#fff' : '#484f58',
              cursor: input.trim() && !isRunning ? 'pointer' : 'not-allowed',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
              transition: 'all 150ms',
            }}
          >
            {isRunning ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
          </button>
        </div>
        <div style={{ textAlign: 'center', marginTop: 8, color: '#484f58', fontSize: 11 }}>
          Commands are reviewed by AI before execution. Destructive operations are blocked.
        </div>
      </div>
    </div>
  );
}
