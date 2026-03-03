import { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Plus, Send, Pause, Play, CheckCircle, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { useSwarm } from '../hooks/useSwarm';
import type { CollaborationMode, CreateSessionRequest, SwarmSession } from '../types/swarm';

// ── Helpers ─────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  active: '#2D8B4E',
  paused: '#D4A017',
  completed: '#2E75B6',
  failed: '#C0392B',
};

const MODE_LABELS: Record<string, string> = {
  round_table: 'Round Table',
  review_chain: 'Review Chain',
  specialist: 'Specialist',
  debate: 'Debate',
};

function formatCost(cost: number): string {
  return cost === 0 ? '$0.00 (local)' : `$${cost.toFixed(4)}`;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── Caste Badge ─────────────────────────────────────────────────────

const CASTE_COLORS: Record<string, string> = {
  guardian_claude: '#7C3AED',
  hydra_code: '#059669',
  hydra_financial: '#D97706',
  ultra_reasoning: '#2563EB',
  ultra_research: '#0891B2',
  mutalisk_legal: '#DC2626',
  mutalisk_conversational: '#EC4899',
  hydra_compliance: '#9333EA',
  hydra_marketing: '#F59E0B',
  nydus: '#6366F1',
};

function CasteBadge({ caste }: { caste: string }) {
  const color = CASTE_COLORS[caste] || '#6B7280';
  const label = caste.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '9999px',
        fontSize: '11px',
        fontWeight: 600,
        color: '#fff',
        background: color,
        marginRight: '4px',
        marginBottom: '4px',
      }}
    >
      {label}
    </span>
  );
}

// ── Create Session Modal ────────────────────────────────────────────

interface CreateModalProps {
  presets: Record<string, string[]>;
  onClose: () => void;
  onCreate: (req: CreateSessionRequest) => Promise<void>;
}

function CreateSessionModal({ presets, onClose, onCreate }: CreateModalProps) {
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [mode, setMode] = useState<CollaborationMode>('round_table');
  const [teamPreset, setTeamPreset] = useState('code');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectName.trim() || !description.trim()) return;
    setSubmitting(true);
    try {
      await onCreate({
        project_name: projectName.trim(),
        description: description.trim(),
        mode,
        team_preset: teamPreset,
        created_by: 'portal-user',
      });
      onClose();
    } catch {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <form
        onClick={e => e.stopPropagation()}
        onSubmit={handleSubmit}
        style={{
          background: 'var(--navy)',
          border: '1px solid #2A3A5C',
          borderRadius: '12px',
          padding: '28px',
          width: '480px',
          maxWidth: '90vw',
        }}
      >
        <h2 style={{ color: '#fff', fontSize: '18px', fontWeight: 700, marginBottom: '20px' }}>
          New Swarm Session
        </h2>

        <label style={{ color: '#8899AA', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
          Project Name
        </label>
        <input
          value={projectName}
          onChange={e => setProjectName(e.target.value)}
          placeholder="e.g. API Refactor Sprint"
          style={{
            width: '100%',
            padding: '10px 12px',
            borderRadius: '8px',
            border: '1px solid #2A3A5C',
            background: 'var(--navy-dark)',
            color: '#fff',
            fontSize: '14px',
            marginBottom: '14px',
            boxSizing: 'border-box',
          }}
        />

        <label style={{ color: '#8899AA', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
          Description / First Prompt
        </label>
        <textarea
          value={description}
          onChange={e => setDescription(e.target.value)}
          rows={3}
          placeholder="Describe what the swarm should work on..."
          style={{
            width: '100%',
            padding: '10px 12px',
            borderRadius: '8px',
            border: '1px solid #2A3A5C',
            background: 'var(--navy-dark)',
            color: '#fff',
            fontSize: '14px',
            marginBottom: '14px',
            resize: 'vertical',
            boxSizing: 'border-box',
          }}
        />

        <div style={{ display: 'flex', gap: '12px', marginBottom: '14px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ color: '#8899AA', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
              Mode
            </label>
            <select
              value={mode}
              onChange={e => setMode(e.target.value as CollaborationMode)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                border: '1px solid #2A3A5C',
                background: 'var(--navy-dark)',
                color: '#fff',
                fontSize: '14px',
              }}
            >
              <option value="round_table">Round Table</option>
              <option value="review_chain">Review Chain</option>
              <option value="specialist">Specialist</option>
              <option value="debate">Debate</option>
            </select>
          </div>

          <div style={{ flex: 1 }}>
            <label style={{ color: '#8899AA', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
              Team Preset
            </label>
            <select
              value={teamPreset}
              onChange={e => setTeamPreset(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                border: '1px solid #2A3A5C',
                background: 'var(--navy-dark)',
                color: '#fff',
                fontSize: '14px',
              }}
            >
              {Object.keys(presets).map(k => (
                <option key={k} value={k}>{k.charAt(0).toUpperCase() + k.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>

        {presets[teamPreset] && (
          <div style={{ marginBottom: '16px' }}>
            <span style={{ color: '#667788', fontSize: '12px' }}>Castes: </span>
            {presets[teamPreset].map(c => <CasteBadge key={c} caste={c} />)}
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: '1px solid #2A3A5C',
              background: 'transparent',
              color: '#8899AA',
              fontSize: '14px',
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!projectName.trim() || !description.trim() || submitting}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              background: submitting ? '#1a5c3a' : '#2D8B4E',
              color: '#fff',
              fontSize: '14px',
              fontWeight: 600,
              cursor: submitting ? 'wait' : 'pointer',
              opacity: (!projectName.trim() || !description.trim()) ? 0.5 : 1,
            }}
          >
            {submitting ? 'Creating...' : 'Create Session'}
          </button>
        </div>
      </form>
    </div>
  );
}

// ── Session Card ────────────────────────────────────────────────────

function SessionCard({
  session,
  isSelected,
  onSelect,
}: {
  session: SwarmSession;
  isSelected: boolean;
  onSelect: (id: string) => void;
}) {
  return (
    <div
      onClick={() => onSelect(session.session_id)}
      style={{
        background: isSelected ? 'var(--navy-light)' : 'var(--navy-dark)',
        border: `1px solid ${isSelected ? 'var(--blue)' : '#2A3A5C'}`,
        borderRadius: '10px',
        padding: '16px',
        cursor: 'pointer',
        transition: 'all 150ms',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
        <h3 style={{ color: '#fff', fontSize: '15px', fontWeight: 600, margin: 0, flex: 1 }}>
          {session.project_name}
        </h3>
        <span
          style={{
            padding: '2px 8px',
            borderRadius: '9999px',
            fontSize: '11px',
            fontWeight: 600,
            color: '#fff',
            background: STATUS_COLORS[session.status] || '#6B7280',
            marginLeft: '8px',
            textTransform: 'uppercase',
          }}
        >
          {session.status}
        </span>
      </div>

      <p style={{ color: '#667788', fontSize: '13px', margin: '0 0 10px 0', lineHeight: 1.4 }}>
        {session.description.length > 100 ? session.description.slice(0, 100) + '...' : session.description}
      </p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
        {session.participating_castes.map(c => <CasteBadge key={c} caste={c} />)}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#667788', fontSize: '12px' }}>
        <span>{MODE_LABELS[session.mode] || session.mode}</span>
        <span>Round {session.current_round} | {session.message_count} msgs</span>
        <span>{formatCost(session.total_cost)}</span>
      </div>
      <div style={{ color: '#556677', fontSize: '11px', marginTop: '4px', textAlign: 'right' }}>
        {timeAgo(session.created_at)}
      </div>
    </div>
  );
}

// ── Main Page ───────────────────────────────────────────────────────

export default function SwarmPage() {
  const {
    sessions, selectedSession, presets, health, loading, sending, error, connected,
    refreshSessions, selectSession, deselectSession, createSession,
    sendMessage, pauseSession, resumeSession, completeSession, loadPresets,
  } = useSwarm();

  const [showCreate, setShowCreate] = useState(false);
  const [messageInput, setMessageInput] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { loadPresets(); }, [loadPresets]);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedSession?.messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim() || sending) return;
    const msg = messageInput;
    setMessageInput('');
    await sendMessage(msg);
  };

  const handleCreate = async (req: CreateSessionRequest) => {
    const session = await createSession(req);
    await selectSession(session.session_id);
  };

  const filteredSessions = statusFilter === 'all'
    ? sessions
    : sessions.filter(s => s.status === statusFilter);

  const activeSessions = sessions.filter(s => s.status === 'active').length;
  const totalCost = sessions.reduce((sum, s) => sum + s.total_cost, 0);

  // ── Session Detail View ───────────────────────────────────────────
  if (selectedSession) {
    return (
      <div style={{ padding: '32px', maxWidth: '900px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <button
            onClick={deselectSession}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              background: 'none', border: '1px solid #2A3A5C', borderRadius: '6px',
              padding: '6px 12px', color: '#8899AA', fontSize: '13px', cursor: 'pointer',
            }}
          >
            <ArrowLeft style={{ width: 14, height: 14 }} /> Back
          </button>
          <h1 style={{ color: 'white', fontSize: '20px', fontWeight: 700, margin: 0, flex: 1 }}>
            {selectedSession.project_name}
          </h1>
          <span
            style={{
              padding: '4px 12px', borderRadius: '9999px', fontSize: '12px',
              fontWeight: 600, color: '#fff',
              background: STATUS_COLORS[selectedSession.status] || '#6B7280',
              textTransform: 'uppercase',
            }}
          >
            {selectedSession.status}
          </span>
        </div>

        {/* Session Info Bar */}
        <div
          style={{
            display: 'flex', gap: '20px', flexWrap: 'wrap',
            padding: '12px 16px', borderRadius: '8px',
            background: 'var(--navy-dark)', border: '1px solid #2A3A5C',
            marginBottom: '16px', fontSize: '13px', color: '#8899AA',
          }}
        >
          <span>Mode: <strong style={{ color: '#fff' }}>{MODE_LABELS[selectedSession.mode]}</strong></span>
          <span>Round: <strong style={{ color: '#fff' }}>{selectedSession.current_round}/{selectedSession.max_rounds}</strong></span>
          <span>Cost: <strong style={{ color: '#fff' }}>{formatCost(selectedSession.total_cost)}</strong></span>
          <span>Messages: <strong style={{ color: '#fff' }}>{selectedSession.message_count}</strong></span>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
            {selectedSession.participating_castes.map(c => <CasteBadge key={c} caste={c} />)}
          </div>
        </div>

        {/* Session Controls */}
        {selectedSession.status !== 'completed' && selectedSession.status !== 'failed' && (
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
            {selectedSession.status === 'active' && (
              <button
                onClick={pauseSession}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  padding: '8px 16px', borderRadius: '8px', border: '1px solid #D4A017',
                  background: 'transparent', color: '#D4A017', fontSize: '13px', cursor: 'pointer',
                }}
              >
                <Pause style={{ width: 14, height: 14 }} /> Pause
              </button>
            )}
            {selectedSession.status === 'paused' && (
              <button
                onClick={resumeSession}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  padding: '8px 16px', borderRadius: '8px', border: '1px solid #2D8B4E',
                  background: 'transparent', color: '#2D8B4E', fontSize: '13px', cursor: 'pointer',
                }}
              >
                <Play style={{ width: 14, height: 14 }} /> Resume
              </button>
            )}
            <button
              onClick={completeSession}
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '8px 16px', borderRadius: '8px', border: '1px solid #2E75B6',
                background: 'transparent', color: '#2E75B6', fontSize: '13px', cursor: 'pointer',
              }}
            >
              <CheckCircle style={{ width: 14, height: 14 }} /> Complete
            </button>
          </div>
        )}

        {/* Messages Timeline */}
        <div
          style={{
            background: 'var(--navy-dark)', border: '1px solid #2A3A5C', borderRadius: '10px',
            padding: '16px', maxHeight: '500px', overflowY: 'auto', marginBottom: '16px',
          }}
        >
          {(!selectedSession.messages || selectedSession.messages.length === 0) && (
            <p style={{ color: '#667788', textAlign: 'center', padding: '40px 0' }}>
              No messages yet. Send a prompt to start the session.
            </p>
          )}
          {selectedSession.messages?.map((msg, i) => (
            <div
              key={msg.message_id || i}
              style={{
                marginBottom: '14px',
                padding: '12px 14px',
                borderRadius: '8px',
                background: msg.role === 'human' ? '#1a2744' : '#111D35',
                borderLeft: `3px solid ${msg.role === 'human' ? '#2E75B6' : (CASTE_COLORS[msg.caste || ''] || '#4B5563')}`,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {msg.caste && <CasteBadge caste={msg.caste} />}
                  <span style={{ color: '#8899AA', fontSize: '12px', fontWeight: 600 }}>
                    {msg.role === 'human' ? 'You' : msg.caste ? '' : 'System'}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '12px', color: '#556677', fontSize: '11px' }}>
                  {msg.model_used && <span>{msg.model_used}</span>}
                  {msg.latency_ms > 0 && <span>{(msg.latency_ms / 1000).toFixed(1)}s</span>}
                  <span>{formatCost(msg.cost)}</span>
                  <span>R{msg.round_number}</span>
                </div>
              </div>
              <div style={{ color: '#D1D5DB', fontSize: '14px', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />

          {sending && (
            <div style={{ textAlign: 'center', padding: '16px', color: '#8899AA', fontSize: '13px' }}>
              <span style={{ animation: 'blink 1s infinite' }}>Castes are responding...</span>
            </div>
          )}
        </div>

        {/* Message Input */}
        {selectedSession.status === 'active' && (
          <form onSubmit={handleSend} style={{ display: 'flex', gap: '10px' }}>
            <input
              value={messageInput}
              onChange={e => setMessageInput(e.target.value)}
              placeholder="Send a message to the swarm..."
              disabled={sending}
              style={{
                flex: 1, padding: '12px 16px', borderRadius: '10px',
                border: '1px solid #2A3A5C', background: 'var(--navy-dark)',
                color: '#fff', fontSize: '14px',
              }}
            />
            <button
              type="submit"
              disabled={!messageInput.trim() || sending}
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '12px 20px', borderRadius: '10px', border: 'none',
                background: sending ? '#1a5c3a' : '#2D8B4E', color: '#fff',
                fontSize: '14px', fontWeight: 600,
                cursor: sending ? 'wait' : 'pointer',
                opacity: !messageInput.trim() ? 0.5 : 1,
              }}
            >
              <Send style={{ width: 16, height: 16 }} /> Send
            </button>
          </form>
        )}
      </div>
    );
  }

  // ── Sessions List View ────────────────────────────────────────────
  return (
    <div style={{ padding: '32px', maxWidth: '900px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ color: 'white', fontSize: '22px', fontWeight: 700, margin: 0 }}>
            Swarm Sessions
          </h1>
          <p style={{ color: '#667788', fontSize: '13px', margin: '4px 0 0 0' }}>
            Multi-model live collaboration
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: connected ? '#2D8B4E' : '#C0392B', fontSize: '13px' }}>
            {connected ? <Wifi style={{ width: 16, height: 16 }} /> : <WifiOff style={{ width: 16, height: 16 }} />}
            {connected ? 'Connected' : 'Offline'}
          </div>
          <button
            onClick={refreshSessions}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '8px 12px', borderRadius: '8px', border: '1px solid #2A3A5C',
              background: 'transparent', color: '#8899AA', fontSize: '13px', cursor: 'pointer',
            }}
          >
            <RefreshCw style={{ width: 14, height: 14 }} />
          </button>
          <button
            onClick={() => setShowCreate(true)}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '10px 18px', borderRadius: '8px', border: 'none',
              background: '#2D8B4E', color: '#fff', fontSize: '14px',
              fontWeight: 600, cursor: 'pointer',
            }}
          >
            <Plus style={{ width: 16, height: 16 }} /> New Session
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '24px' }}>
        {[
          { label: 'Active Sessions', value: String(activeSessions), color: '#2D8B4E' },
          { label: 'Total Sessions', value: String(sessions.length), color: '#2E75B6' },
          { label: 'Total Cost', value: formatCost(totalCost), color: '#D4A017' },
          { label: 'Swarm Health', value: health?.status === 'ok' ? 'Healthy' : 'Unknown', color: connected ? '#2D8B4E' : '#C0392B' },
        ].map(card => (
          <div
            key={card.label}
            style={{
              background: 'var(--navy-dark)', border: '1px solid #2A3A5C', borderRadius: '10px',
              padding: '16px', textAlign: 'center',
            }}
          >
            <p style={{ color: '#667788', fontSize: '12px', margin: '0 0 6px 0' }}>{card.label}</p>
            <p style={{ color: card.color, fontSize: '20px', fontWeight: 700, margin: 0 }}>{card.value}</p>
          </div>
        ))}
      </div>

      {/* Status Filter */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        {['all', 'active', 'paused', 'completed'].map(f => (
          <button
            key={f}
            onClick={() => setStatusFilter(f)}
            style={{
              padding: '6px 14px', borderRadius: '9999px', border: '1px solid #2A3A5C',
              background: statusFilter === f ? 'var(--navy-light)' : 'transparent',
              color: statusFilter === f ? '#fff' : '#8899AA',
              fontSize: '13px', cursor: 'pointer', textTransform: 'capitalize',
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div style={{
          padding: '12px 16px', borderRadius: '8px', marginBottom: '16px',
          background: 'rgba(192, 57, 43, 0.15)', border: '1px solid #C0392B', color: '#E74C3C', fontSize: '13px',
        }}>
          {error}
        </div>
      )}

      {/* Sessions Grid */}
      {loading && sessions.length === 0 ? (
        <p style={{ color: '#667788', textAlign: 'center', padding: '40px 0' }}>Loading sessions...</p>
      ) : filteredSessions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <p style={{ color: '#667788', fontSize: '15px', marginBottom: '12px' }}>
            {sessions.length === 0 ? 'No sessions yet.' : 'No sessions match this filter.'}
          </p>
          {sessions.length === 0 && (
            <button
              onClick={() => setShowCreate(true)}
              style={{
                padding: '10px 20px', borderRadius: '8px', border: 'none',
                background: '#2D8B4E', color: '#fff', fontSize: '14px',
                fontWeight: 600, cursor: 'pointer',
              }}
            >
              Create Your First Session
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '14px' }}>
          {filteredSessions.map(s => (
            <SessionCard
              key={s.session_id}
              session={s}
              isSelected={false}
              onSelect={selectSession}
            />
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <CreateSessionModal
          presets={presets}
          onClose={() => setShowCreate(false)}
          onCreate={handleCreate}
        />
      )}
    </div>
  );
}
