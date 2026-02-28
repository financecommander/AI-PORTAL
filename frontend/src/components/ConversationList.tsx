import { useState, useEffect } from 'react';
import { MessageSquare, Plus, Trash2 } from 'lucide-react';
import { api } from '../api/client';

interface Conversation {
  id: string;
  title: string;
  updated_at: string;
  message_count: number;
}

interface ConversationListProps {
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
}

export default function ConversationList({ activeId, onSelect, onNew }: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchConversations = async () => {
    try {
      const data = await api.request<{ conversations: Conversation[] }>('/conversations/');
      setConversations(data.conversations || []);
    } catch {
      console.error('Failed to fetch conversations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchConversations(); }, []);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.request(`/conversations/${id}`, { method: 'DELETE' });
      setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch { console.error('Failed to delete'); }
  };

  if (loading) {
    return <div style={{ padding: '12px', color: 'var(--cr-text-muted)', fontSize: 12, textAlign: 'center' }}>Loading...</div>;
  }

  return (
    <div>
      <button
        onClick={onNew}
        style={{
          display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '8px 12px',
          marginBottom: 4, borderRadius: 'var(--cr-radius-sm)', border: '1px dashed var(--cr-border)',
          background: 'transparent', color: 'var(--cr-text-muted)', fontSize: 12, cursor: 'pointer',
          transition: 'all 120ms',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; e.currentTarget.style.color = 'var(--cr-green-600)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; e.currentTarget.style.color = 'var(--cr-text-muted)'; }}
      >
        <Plus size={14} /> New conversation
      </button>
      {conversations.map((c) => (
        <button
          key={c.id}
          onClick={() => onSelect(c.id)}
          style={{
            display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '8px 12px',
            marginBottom: 2, borderRadius: 'var(--cr-radius-sm)', border: 'none',
            background: activeId === c.id ? 'var(--cr-surface)' : 'transparent',
            cursor: 'pointer', textAlign: 'left', transition: 'background 100ms',
            position: 'relative',
          }}
          onMouseEnter={(e) => { if (activeId !== c.id) e.currentTarget.style.background = 'var(--cr-surface-2)'; }}
          onMouseLeave={(e) => { if (activeId !== c.id) e.currentTarget.style.background = 'transparent'; }}
        >
          <MessageSquare style={{ width: 14, height: 14, color: 'var(--cr-text-muted)', flexShrink: 0 }} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 12, color: activeId === c.id ? 'var(--cr-green-900)' : 'var(--cr-text-secondary)', fontWeight: activeId === c.id ? 500 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {c.title || 'New conversation'}
            </div>
          </div>
          <button
            onClick={(e) => handleDelete(e, c.id)}
            style={{ opacity: 0, position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--cr-text-muted)', padding: 4 }}
            onMouseEnter={(e) => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.color = 'var(--cr-danger)'; }}
          >
            <Trash2 size={12} />
          </button>
        </button>
      ))}
      {conversations.length === 0 && (
        <div style={{ padding: '12px', color: 'var(--cr-text-dim)', fontSize: 11, textAlign: 'center' }}>No conversations yet</div>
      )}
    </div>
  );
}

