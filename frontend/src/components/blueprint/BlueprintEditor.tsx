/**
 * Blueprint Editor — Visual .orc workflow designer for the Swarm Mainframe.
 *
 * Embedded in the AI-PORTAL SwarmPage as an authenticated session-aware panel.
 * Provides a split-pane layout: visual graph editor (left) + .orc code editor (right).
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  ArrowLeft, Plus, Play, Save, CheckCircle, AlertTriangle,
  Code, Layout, Trash2, Download, Upload, Zap, Settings,
  ChevronRight, X, FileText, Cpu,
} from 'lucide-react';
import { useBlueprint } from '../../hooks/useBlueprint';
import type {
  BlueprintNode, BlueprintGraph, BlueprintSession,
  CreateBlueprintRequest, TritonModel,
} from '../../types/blueprint';

// ── Constants ───────────────────────────────────────────────────────

const NODE_COLORS: Record<string, string> = {
  workflow: '#1A6B3C',
  step: '#2E75B6',
  parallel: '#7C3AED',
  guard: '#D97706',
  budget: '#059669',
  quality_gate: '#0891B2',
  circuit_breaker: '#DC2626',
  if: '#9333EA',
  match: '#6366F1',
  try: '#F59E0B',
  finally: '#EC4899',
  for_each: '#14B8A6',
};

const BLOCK_TYPES = [
  { type: 'step', label: 'Step', icon: '▶' },
  { type: 'parallel', label: 'Parallel', icon: '⫘' },
  { type: 'if', label: 'Condition', icon: '◇' },
  { type: 'try', label: 'Try/Catch', icon: '⚡' },
  { type: 'guard', label: 'Guard', icon: '🛡' },
  { type: 'budget', label: 'Budget', icon: '💰' },
  { type: 'quality_gate', label: 'Quality Gate', icon: '✓' },
  { type: 'circuit_breaker', label: 'Circuit Breaker', icon: '⚙' },
  { type: 'finally', label: 'Finally', icon: '🏁' },
  { type: 'match', label: 'Match', icon: '🔀' },
  { type: 'for_each', label: 'For Each', icon: '🔄' },
];

const STATUS_COLORS: Record<string, string> = {
  draft: '#6B7280',
  validating: '#D4A017',
  executing: '#2E75B6',
  completed: '#1A6B3C',
  failed: '#D64545',
  paused: '#D4A017',
};

// ── Utility ─────────────────────────────────────────────────────────

let nodeCounter = 0;
function nextId(prefix = 'node'): string {
  return `${prefix}_${++nodeCounter}_${Date.now().toString(36)}`;
}

// ── Session List View ───────────────────────────────────────────────

function BlueprintSessionList({
  sessions,
  loading,
  onSelect,
  onCreate,
  onDelete,
}: {
  sessions: BlueprintSession[];
  loading: boolean;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
}) {
  return (
    <div style={{ padding: '32px', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h2 style={{ color: 'var(--cr-text)', fontSize: '20px', fontWeight: 700, margin: 0 }}>
            Blueprint Sessions
          </h2>
          <p style={{ color: 'var(--cr-text-muted)', fontSize: '13px', margin: '4px 0 0' }}>
            Visual workflow designer for Orchestra .orc files
          </p>
        </div>
        <button
          onClick={onCreate}
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)',
            background: 'var(--cr-green-700)', color: '#fff',
            border: 'none', fontSize: '13px', fontWeight: 600, cursor: 'pointer',
          }}
        >
          <Plus style={{ width: 14, height: 14 }} /> New Blueprint
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--cr-text-muted)' }}>Loading sessions...</div>
      ) : sessions.length === 0 ? (
        <div style={{
          textAlign: 'center', padding: '60px 20px',
          background: 'var(--cr-surface-2)', borderRadius: 'var(--cr-radius-md)',
          border: '1px solid var(--cr-border)',
        }}>
          <Layout style={{ width: 48, height: 48, color: 'var(--cr-text-muted)', marginBottom: '16px' }} />
          <h3 style={{ color: 'var(--cr-text)', fontSize: '16px', margin: '0 0 8px' }}>No blueprints yet</h3>
          <p style={{ color: 'var(--cr-text-muted)', fontSize: '13px', margin: 0 }}>
            Create your first Orchestra workflow blueprint
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {sessions.map(s => (
            <div
              key={s.session_id}
              onClick={() => onSelect(s.session_id)}
              style={{
                display: 'flex', alignItems: 'center', gap: '12px',
                padding: '16px', borderRadius: 'var(--cr-radius-sm)',
                background: 'var(--cr-surface-2)', border: '1px solid var(--cr-border)',
                cursor: 'pointer', transition: 'border-color 0.15s',
              }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--cr-green-700)')}
              onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--cr-border)')}
            >
              <FileText style={{ width: 20, height: 20, color: 'var(--cr-green-700)', flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ color: 'var(--cr-text)', fontSize: '14px', fontWeight: 600 }}>{s.name}</div>
                {s.description && (
                  <div style={{ color: 'var(--cr-text-muted)', fontSize: '12px', marginTop: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {s.description}
                  </div>
                )}
              </div>
              <span style={{
                padding: '4px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600,
                color: '#fff', background: STATUS_COLORS[s.status] || '#6B7280', textTransform: 'uppercase',
              }}>
                {s.status}
              </span>
              <button
                onClick={e => { e.stopPropagation(); onDelete(s.session_id); }}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--cr-text-muted)', padding: '4px' }}
                title="Delete"
              >
                <Trash2 style={{ width: 14, height: 14 }} />
              </button>
              <ChevronRight style={{ width: 16, height: 16, color: 'var(--cr-text-muted)' }} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Create Blueprint Modal ──────────────────────────────────────────

function CreateBlueprintModal({
  onClose,
  onCreate,
}: {
  onClose: () => void;
  onCreate: (req: CreateBlueprintRequest) => Promise<void>;
}) {
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    await onCreate({ name: name.trim(), description: desc.trim() });
    setCreating(false);
    onClose();
  };

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)' }} onClick={onClose} />
      <form
        onSubmit={handleSubmit}
        style={{
          position: 'relative', width: '420px', padding: '28px',
          background: 'var(--cr-panel)', borderRadius: 'var(--cr-radius-md)',
          border: '1px solid var(--cr-border)', boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ margin: 0, color: 'var(--cr-text)', fontSize: '16px' }}>New Blueprint</h3>
          <button type="button" onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--cr-text-muted)' }}>
            <X style={{ width: 18, height: 18 }} />
          </button>
        </div>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--cr-text-secondary)', marginBottom: '6px' }}>
            Workflow Name
          </label>
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="e.g. credit_analysis_pipeline"
            required
            style={{
              width: '100%', padding: '10px 12px', fontSize: '14px',
              border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)',
              background: 'var(--cr-surface-2)', color: 'var(--cr-text)',
              outline: 'none', boxSizing: 'border-box',
            }}
          />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--cr-text-secondary)', marginBottom: '6px' }}>
            Description
          </label>
          <textarea
            value={desc}
            onChange={e => setDesc(e.target.value)}
            placeholder="What does this workflow do?"
            rows={3}
            style={{
              width: '100%', padding: '10px 12px', fontSize: '14px',
              border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)',
              background: 'var(--cr-surface-2)', color: 'var(--cr-text)',
              outline: 'none', resize: 'vertical', boxSizing: 'border-box',
            }}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
          <button type="button" onClick={onClose} style={{
            padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)',
            border: '1px solid var(--cr-border)', background: 'transparent',
            color: 'var(--cr-text-secondary)', fontSize: '13px', cursor: 'pointer',
          }}>
            Cancel
          </button>
          <button type="submit" disabled={creating || !name.trim()} style={{
            padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)',
            background: 'var(--cr-green-700)', color: '#fff',
            border: 'none', fontSize: '13px', fontWeight: 600, cursor: 'pointer',
            opacity: creating || !name.trim() ? 0.5 : 1,
          }}>
            {creating ? 'Creating...' : 'Create Blueprint'}
          </button>
        </div>
      </form>
    </div>
  );
}

// ── Visual Graph Canvas ─────────────────────────────────────────────

function GraphCanvas({
  graph,
  selectedNodeId,
  onSelectNode,
  onMoveNode,
  onDeleteNode,
}: {
  graph: BlueprintGraph;
  selectedNodeId: string | null;
  onSelectNode: (id: string | null) => void;
  onMoveNode: (id: string, x: number, y: number) => void;
  onDeleteNode: (id: string) => void;
}) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<{ id: string; offsetX: number; offsetY: number } | null>(null);

  const handleMouseDown = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    const node = graph.nodes.find(n => n.id === nodeId);
    if (!node) return;
    dragRef.current = {
      id: nodeId,
      offsetX: e.clientX - node.position.x,
      offsetY: e.clientY - node.position.y,
    };
    onSelectNode(nodeId);
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!dragRef.current) return;
    onMoveNode(dragRef.current.id, e.clientX - dragRef.current.offsetX, e.clientY - dragRef.current.offsetY);
  }, [onMoveNode]);

  const handleMouseUp = useCallback(() => { dragRef.current = null; }, []);

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  return (
    <div
      ref={canvasRef}
      onClick={() => onSelectNode(null)}
      style={{
        flex: 1, position: 'relative', overflow: 'auto',
        background: 'var(--cr-surface-1)',
        backgroundImage: 'radial-gradient(circle, var(--cr-border) 1px, transparent 1px)',
        backgroundSize: '20px 20px',
        minHeight: '400px',
      }}
    >
      {/* Edges (SVG overlay) */}
      <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
        {graph.edges.map(edge => {
          const src = graph.nodes.find(n => n.id === edge.source);
          const tgt = graph.nodes.find(n => n.id === edge.target);
          if (!src || !tgt) return null;
          const x1 = src.position.x + 90;
          const y1 = src.position.y + 30;
          const x2 = tgt.position.x + 90;
          const y2 = tgt.position.y + 30;
          return (
            <g key={edge.id}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--cr-green-700)" strokeWidth={2} strokeDasharray={edge.edge_type === 'conditional' ? '6,3' : 'none'} opacity={0.6} />
              {/* Arrow head */}
              <circle cx={x2} cy={y2} r={4} fill="var(--cr-green-700)" opacity={0.6} />
            </g>
          );
        })}
      </svg>

      {/* Nodes */}
      {graph.nodes.map(node => {
        const color = NODE_COLORS[node.type] || '#6B7280';
        const selected = node.id === selectedNodeId;
        return (
          <div
            key={node.id}
            onMouseDown={e => handleMouseDown(e, node.id)}
            style={{
              position: 'absolute',
              left: node.position.x,
              top: node.position.y,
              width: 180,
              minHeight: 56,
              borderRadius: '8px',
              background: 'var(--cr-panel)',
              border: `2px solid ${selected ? color : 'var(--cr-border)'}`,
              boxShadow: selected ? `0 0 0 3px ${color}33` : '0 2px 8px rgba(0,0,0,0.1)',
              cursor: 'grab',
              userSelect: 'none',
              zIndex: selected ? 10 : 1,
            }}
          >
            {/* Node header */}
            <div style={{
              padding: '8px 10px', borderBottom: `1px solid ${selected ? color + '40' : 'var(--cr-border)'}`,
              display: 'flex', alignItems: 'center', gap: '6px',
            }}>
              <span style={{
                width: 8, height: 8, borderRadius: '50%', background: color,
                display: 'inline-block', flexShrink: 0,
              }} />
              <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--cr-text)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {node.label}
              </span>
              <span style={{ fontSize: '9px', color: 'var(--cr-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                {node.type}
              </span>
            </div>
            {/* Node body — show key properties */}
            <div style={{ padding: '6px 10px', fontSize: '11px', color: 'var(--cr-text-muted)' }}>
              {node.properties.agent && <div>agent: {String(node.properties.agent)}</div>}
              {node.properties.prompt && (
                <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '160px' }}>
                  prompt: {String(node.properties.prompt).slice(0, 40)}
                </div>
              )}
            </div>
          </div>
        );
      })}

      {graph.nodes.length === 0 && (
        <div style={{
          position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
          textAlign: 'center', color: 'var(--cr-text-muted)', fontSize: '14px',
        }}>
          <Layout style={{ width: 32, height: 32, marginBottom: '8px', opacity: 0.5 }} />
          <div>Drag blocks from the sidebar or write .orc code</div>
        </div>
      )}
    </div>
  );
}

// ── Code Editor Panel ───────────────────────────────────────────────

function CodeEditor({
  source,
  onChange,
  validation,
  saving,
}: {
  source: string;
  onChange: (source: string) => void;
  validation: { valid: boolean; errors: string[]; warnings?: string[] } | null;
  saving: boolean;
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{
        padding: '8px 12px', borderBottom: '1px solid var(--cr-border)',
        display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px',
        background: 'var(--cr-surface-2)',
      }}>
        <Code style={{ width: 14, height: 14, color: 'var(--cr-green-700)' }} />
        <span style={{ color: 'var(--cr-text)', fontWeight: 600 }}>.orc Source</span>
        {saving && <span style={{ color: 'var(--cr-text-muted)', marginLeft: 'auto' }}>Saving...</span>}
        {validation && (
          <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '4px' }}>
            {validation.valid ? (
              <><CheckCircle style={{ width: 12, height: 12, color: '#1A6B3C' }} /> <span style={{ color: '#1A6B3C' }}>Valid</span></>
            ) : (
              <><AlertTriangle style={{ width: 12, height: 12, color: '#D64545' }} /> <span style={{ color: '#D64545' }}>{validation.errors.length} error{validation.errors.length !== 1 ? 's' : ''}</span></>
            )}
          </span>
        )}
      </div>
      <textarea
        value={source}
        onChange={e => onChange(e.target.value)}
        spellCheck={false}
        style={{
          flex: 1, width: '100%', padding: '12px', fontSize: '13px',
          fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
          lineHeight: '1.6', background: 'var(--cr-surface-1)',
          color: 'var(--cr-text)', border: 'none', outline: 'none',
          resize: 'none', boxSizing: 'border-box',
        }}
        placeholder={`workflow my_pipeline {\n    step analyze {\n        agent: "gpt-4"\n        prompt: "Analyze the input data"\n    }\n}`}
      />
      {/* Validation errors */}
      {validation && !validation.valid && (
        <div style={{
          padding: '8px 12px', borderTop: '1px solid var(--cr-border)',
          background: '#D6454510', maxHeight: '100px', overflowY: 'auto',
        }}>
          {validation.errors.map((err, i) => (
            <div key={i} style={{ fontSize: '12px', color: '#D64545', padding: '2px 0' }}>
              <AlertTriangle style={{ width: 11, height: 11, display: 'inline', marginRight: '4px' }} />
              {err}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Properties Panel ────────────────────────────────────────────────

function PropertiesPanel({
  node,
  models,
  onUpdate,
  onDelete,
}: {
  node: BlueprintNode | null;
  models: TritonModel[];
  onUpdate: (id: string, props: Record<string, unknown>) => void;
  onDelete: (id: string) => void;
}) {
  if (!node) {
    return (
      <div style={{ padding: '16px', color: 'var(--cr-text-muted)', fontSize: '13px', textAlign: 'center' }}>
        Select a node to edit properties
      </div>
    );
  }

  const color = NODE_COLORS[node.type] || '#6B7280';

  return (
    <div style={{ padding: '12px', overflow: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <span style={{ width: 10, height: 10, borderRadius: '50%', background: color }} />
        <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--cr-text)' }}>{node.label}</span>
        <span style={{ fontSize: '10px', color: 'var(--cr-text-muted)', textTransform: 'uppercase' }}>{node.type}</span>
      </div>

      {/* Label */}
      <div style={{ marginBottom: '12px' }}>
        <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--cr-text-secondary)', marginBottom: '4px' }}>Label</label>
        <input
          value={node.label}
          onChange={e => onUpdate(node.id, { ...node.properties, __label: e.target.value })}
          style={{
            width: '100%', padding: '6px 8px', fontSize: '12px',
            border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)',
            background: 'var(--cr-surface-2)', color: 'var(--cr-text)', boxSizing: 'border-box',
          }}
        />
      </div>

      {/* Agent selector for step nodes */}
      {node.type === 'step' && (
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--cr-text-secondary)', marginBottom: '4px' }}>Agent</label>
          <input
            value={String(node.properties.agent || '')}
            onChange={e => onUpdate(node.id, { ...node.properties, agent: e.target.value })}
            placeholder="e.g. gpt-4, claude-3-opus, triton_ternary(...)"
            style={{
              width: '100%', padding: '6px 8px', fontSize: '12px',
              border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)',
              background: 'var(--cr-surface-2)', color: 'var(--cr-text)', boxSizing: 'border-box',
            }}
          />
          {models.length > 0 && (
            <div style={{ marginTop: '6px' }}>
              <div style={{ fontSize: '10px', fontWeight: 600, color: 'var(--cr-text-muted)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Cpu style={{ width: 10, height: 10 }} /> Triton Models
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {models.slice(0, 6).map(m => (
                  <button
                    key={m.name}
                    onClick={() => onUpdate(node.id, { ...node.properties, agent: `triton_ternary("${m.name}")` })}
                    title={`${m.description}\n${m.latency} | ${m.accuracy}`}
                    style={{
                      padding: '2px 6px', fontSize: '10px', borderRadius: '4px',
                      border: '1px solid var(--cr-border)', background: 'var(--cr-surface-2)',
                      color: 'var(--cr-text-secondary)', cursor: 'pointer',
                    }}
                  >
                    {m.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Prompt for step nodes */}
      {node.type === 'step' && (
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: 'var(--cr-text-secondary)', marginBottom: '4px' }}>Prompt</label>
          <textarea
            value={String(node.properties.prompt || '')}
            onChange={e => onUpdate(node.id, { ...node.properties, prompt: e.target.value })}
            rows={4}
            style={{
              width: '100%', padding: '6px 8px', fontSize: '12px',
              border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)',
              background: 'var(--cr-surface-2)', color: 'var(--cr-text)',
              resize: 'vertical', boxSizing: 'border-box',
            }}
          />
        </div>
      )}

      {/* Delete button */}
      <button
        onClick={() => onDelete(node.id)}
        style={{
          display: 'flex', alignItems: 'center', gap: '6px', marginTop: '16px',
          padding: '6px 12px', borderRadius: 'var(--cr-radius-xs)',
          border: '1px solid #D64545', background: 'transparent',
          color: '#D64545', fontSize: '12px', cursor: 'pointer',
        }}
      >
        <Trash2 style={{ width: 12, height: 12 }} /> Delete Node
      </button>
    </div>
  );
}

// ── Main Blueprint Editor ───────────────────────────────────────────

export default function BlueprintEditor({ onBack }: { onBack: () => void }) {
  const {
    sessions, activeSession, models, loading, saving, error, validation, execution,
    refreshSessions, selectSession, deselectSession, createSession,
    updateOrcSource, updateGraph, deleteSession,
    parseOrc, generateOrc, validate, execute, loadModels,
  } = useBlueprint();

  const [showCreate, setShowCreate] = useState(false);
  const [view, setView] = useState<'split' | 'code' | 'graph'>('split');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [localSource, setLocalSource] = useState('');
  const [localGraph, setLocalGraph] = useState<BlueprintGraph>({ nodes: [], edges: [], metadata: {} });

  // Load Triton models on mount
  useEffect(() => { loadModels(); }, [loadModels]);

  // Sync local state from active session
  useEffect(() => {
    if (activeSession) {
      setLocalSource(activeSession.orc_source || '');
      setLocalGraph(activeSession.graph || { nodes: [], edges: [], metadata: {} });
    }
  }, [activeSession]);

  // Auto-save debounce for .orc source
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const handleSourceChange = (source: string) => {
    setLocalSource(source);
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => { updateOrcSource(source); }, 1500);
  };

  // Sync code → graph
  const handleSyncToGraph = async () => {
    if (!localSource.trim()) return;
    const graph = await parseOrc(localSource);
    if (graph) setLocalGraph(graph);
  };

  // Sync graph → code
  const handleSyncToCode = async () => {
    if (localGraph.nodes.length === 0) return;
    const source = await generateOrc(localGraph);
    if (source) setLocalSource(source);
  };

  // Validate
  const handleValidate = () => { if (localSource.trim()) validate(localSource); };

  // Execute
  const handleExecute = async () => {
    if (!activeSession) return;
    await updateOrcSource(localSource);
    await execute();
  };

  // Add block from sidebar
  const handleAddBlock = (type: string) => {
    const node: BlueprintNode = {
      id: nextId(type),
      type: type as BlueprintNode['type'],
      label: `${type}_${localGraph.nodes.filter(n => n.type === type).length + 1}`,
      position: { x: 40 + Math.random() * 200, y: 40 + localGraph.nodes.length * 80 },
      properties: {},
      children: [],
    };
    setLocalGraph(prev => ({ ...prev, nodes: [...prev.nodes, node] }));
  };

  // Move node
  const handleMoveNode = useCallback((id: string, x: number, y: number) => {
    setLocalGraph(prev => ({
      ...prev,
      nodes: prev.nodes.map(n => n.id === id ? { ...n, position: { x, y } } : n),
    }));
  }, []);

  // Delete node
  const handleDeleteNode = (id: string) => {
    setLocalGraph(prev => ({
      ...prev,
      nodes: prev.nodes.filter(n => n.id !== id),
      edges: prev.edges.filter(e => e.source !== id && e.target !== id),
    }));
    if (selectedNodeId === id) setSelectedNodeId(null);
  };

  // Update node properties
  const handleUpdateNodeProps = (id: string, props: Record<string, unknown>) => {
    const newLabel = props.__label as string | undefined;
    setLocalGraph(prev => ({
      ...prev,
      nodes: prev.nodes.map(n => {
        if (n.id !== id) return n;
        const { __label, ...rest } = props;
        return { ...n, label: newLabel ?? n.label, properties: rest };
      }),
    }));
  };

  // Handle create
  const handleCreate = async (req: CreateBlueprintRequest) => {
    await createSession(req);
    setShowCreate(false);
  };

  const selectedNode = localGraph.nodes.find(n => n.id === selectedNodeId) || null;

  // ── Session List View ──────────────────────────────────────────
  if (!activeSession) {
    return (
      <div>
        <div style={{ padding: '12px 32px', borderBottom: '1px solid var(--cr-border)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button onClick={onBack} style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'none', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)', padding: '6px 12px', color: 'var(--cr-text-secondary)', fontSize: '13px', cursor: 'pointer' }}>
            <ArrowLeft style={{ width: 14, height: 14 }} /> Swarm Console
          </button>
          <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--cr-text)' }}>Blueprint Editor</span>
        </div>
        <BlueprintSessionList
          sessions={sessions}
          loading={loading}
          onSelect={selectSession}
          onCreate={() => setShowCreate(true)}
          onDelete={deleteSession}
        />
        {showCreate && <CreateBlueprintModal onClose={() => setShowCreate(false)} onCreate={handleCreate} />}
      </div>
    );
  }

  // ── Editor View ────────────────────────────────────────────────
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Toolbar */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        padding: '8px 16px', borderBottom: '1px solid var(--cr-border)',
        background: 'var(--cr-panel)', flexShrink: 0,
      }}>
        <button onClick={() => { deselectSession(); }} style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'none', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)', padding: '6px 10px', color: 'var(--cr-text-secondary)', fontSize: '12px', cursor: 'pointer' }}>
          <ArrowLeft style={{ width: 12, height: 12 }} /> Back
        </button>
        <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--cr-text)', flex: 0 }}>{activeSession.name}</span>
        <span style={{ padding: '3px 8px', borderRadius: '9999px', fontSize: '10px', fontWeight: 600, color: '#fff', background: STATUS_COLORS[activeSession.status] || '#6B7280', textTransform: 'uppercase' }}>
          {activeSession.status}
        </span>

        <div style={{ flex: 1 }} />

        {/* View toggles */}
        <div style={{ display: 'flex', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)', overflow: 'hidden' }}>
          {(['split', 'graph', 'code'] as const).map(v => (
            <button
              key={v}
              onClick={() => setView(v)}
              style={{
                padding: '5px 12px', fontSize: '11px', fontWeight: 600, cursor: 'pointer',
                border: 'none', background: view === v ? 'var(--cr-green-700)' : 'transparent',
                color: view === v ? '#fff' : 'var(--cr-text-secondary)',
                textTransform: 'capitalize',
              }}
            >
              {v === 'split' ? '⫘ Split' : v === 'graph' ? '⬡ Graph' : '</> Code'}
            </button>
          ))}
        </div>

        <button onClick={handleSyncToGraph} title="Sync code → graph" style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 10px', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)', background: 'transparent', color: 'var(--cr-text-secondary)', fontSize: '11px', cursor: 'pointer' }}>
          <Download style={{ width: 12, height: 12 }} /> Parse
        </button>
        <button onClick={handleSyncToCode} title="Sync graph → code" style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 10px', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)', background: 'transparent', color: 'var(--cr-text-secondary)', fontSize: '11px', cursor: 'pointer' }}>
          <Upload style={{ width: 12, height: 12 }} /> Generate
        </button>
        <button onClick={handleValidate} style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 10px', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)', background: 'transparent', color: '#D4A017', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}>
          <CheckCircle style={{ width: 12, height: 12 }} /> Validate
        </button>
        <button onClick={handleExecute} disabled={!validation?.valid} style={{
          display: 'flex', alignItems: 'center', gap: '4px',
          padding: '6px 14px', borderRadius: 'var(--cr-radius-xs)',
          background: validation?.valid ? 'var(--cr-green-700)' : 'var(--cr-surface-2)',
          color: validation?.valid ? '#fff' : 'var(--cr-text-muted)',
          border: 'none', fontSize: '11px', fontWeight: 600, cursor: validation?.valid ? 'pointer' : 'not-allowed',
        }}>
          <Play style={{ width: 12, height: 12 }} /> Execute
        </button>
      </div>

      {/* Execution status banner */}
      {execution && (
        <div style={{
          padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '12px',
          background: execution.status === 'completed' ? '#1A6B3C15' : execution.status === 'failed' ? '#D6454515' : '#2E75B615',
          borderBottom: '1px solid var(--cr-border)', fontSize: '12px',
        }}>
          <Zap style={{ width: 14, height: 14, color: execution.status === 'completed' ? '#1A6B3C' : execution.status === 'failed' ? '#D64545' : '#2E75B6' }} />
          <span style={{ color: 'var(--cr-text)' }}>
            Execution: <strong>{execution.status}</strong>
            {execution.current_step && <> — Step: {execution.current_step}</>}
          </span>
          <div style={{ flex: 1 }} />
          <span style={{ color: 'var(--cr-text-muted)' }}>Progress: {Math.round(execution.progress * 100)}%</span>
          <span style={{ color: 'var(--cr-text-muted)' }}>Cost: ${execution.total_cost.toFixed(4)}</span>
        </div>
      )}

      {/* Main editor area */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Block sidebar */}
        {view !== 'code' && (
          <div style={{
            width: '140px', borderRight: '1px solid var(--cr-border)',
            padding: '8px', overflowY: 'auto', background: 'var(--cr-panel)', flexShrink: 0,
          }}>
            <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--cr-text-muted)', textTransform: 'uppercase', marginBottom: '8px', padding: '0 4px' }}>
              Blocks
            </div>
            {BLOCK_TYPES.map(b => (
              <button
                key={b.type}
                onClick={() => handleAddBlock(b.type)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px', width: '100%',
                  padding: '8px', marginBottom: '4px', borderRadius: 'var(--cr-radius-xs)',
                  border: '1px solid var(--cr-border)', background: 'var(--cr-surface-2)',
                  color: 'var(--cr-text)', fontSize: '11px', cursor: 'pointer', textAlign: 'left',
                }}
              >
                <span>{b.icon}</span>
                <span>{b.label}</span>
              </button>
            ))}
          </div>
        )}

        {/* Graph canvas */}
        {(view === 'split' || view === 'graph') && (
          <GraphCanvas
            graph={localGraph}
            selectedNodeId={selectedNodeId}
            onSelectNode={setSelectedNodeId}
            onMoveNode={handleMoveNode}
            onDeleteNode={handleDeleteNode}
          />
        )}

        {/* Code editor */}
        {(view === 'split' || view === 'code') && (
          <div style={{
            width: view === 'split' ? '40%' : '100%',
            borderLeft: view === 'split' ? '1px solid var(--cr-border)' : 'none',
            display: 'flex', flexDirection: 'column',
          }}>
            <CodeEditor
              source={localSource}
              onChange={handleSourceChange}
              validation={validation}
              saving={saving}
            />
          </div>
        )}

        {/* Properties panel */}
        {view !== 'code' && selectedNodeId && (
          <div style={{
            width: '220px', borderLeft: '1px solid var(--cr-border)',
            background: 'var(--cr-panel)', flexShrink: 0, overflowY: 'auto',
          }}>
            <PropertiesPanel
              node={selectedNode}
              models={models}
              onUpdate={handleUpdateNodeProps}
              onDelete={handleDeleteNode}
            />
          </div>
        )}
      </div>

      {/* Error bar */}
      {error && (
        <div style={{
          padding: '8px 16px', background: '#D6454515', borderTop: '1px solid #D6454540',
          display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#D64545',
        }}>
          <AlertTriangle style={{ width: 14, height: 14 }} />
          {error}
        </div>
      )}
    </div>
  );
}
