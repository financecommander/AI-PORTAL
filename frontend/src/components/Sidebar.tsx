import { useContext } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Bot,
  Layers,
  BarChart3,
  LogOut,
  Settings,
} from 'lucide-react';
import { AuthContext } from '../contexts/AuthContext';
import ConversationList from './ConversationList';

interface SidebarProps {
  activeConversationId?: string | null;
  onSelectConversation?: (id: string) => void;
  onNewConversation?: () => void;
}

const NAV_ITEMS = [
  { label: 'Chat', icon: MessageSquare, path: '/' },
  { label: 'Specialists', icon: Bot, path: '/specialists' },
  { label: 'Pipelines', icon: Layers, path: '/pipelines' },
  { label: 'Usage', icon: BarChart3, path: '/usage' },
];

export default function Sidebar({
  activeConversationId,
  onSelectConversation,
  onNewConversation,
}: SidebarProps) {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--cr-white)',
        borderRight: '1px solid var(--cr-border)',
        flexShrink: 0,
      }}
    >
      {/* Brand */}
      <div style={{ padding: '20px 20px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: 'var(--cr-green-900)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              fontSize: 14,
              fontWeight: 700,
              fontFamily: "'Space Grotesk', sans-serif",
            }}
          >
            C
          </div>
          <div>
            <div
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 600,
                fontSize: 15,
                color: 'var(--cr-text)',
                lineHeight: 1.2,
              }}
            >
              Calculus Research
            </div>
            <div style={{ fontSize: 10, color: 'var(--cr-text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              Financial Innovations
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ padding: '0 12px' }}>
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                width: '100%',
                padding: '10px 12px',
                marginBottom: 2,
                borderRadius: 'var(--cr-radius-sm)',
                border: 'none',
                background: isActive ? 'var(--cr-surface)' : 'transparent',
                cursor: 'pointer',
                transition: 'all 120ms',
                color: isActive ? 'var(--cr-green-900)' : 'var(--cr-text-secondary)',
                fontWeight: isActive ? 600 : 400,
                fontSize: 14,
              }}
            >
              <Icon style={{ width: 18, height: 18 }} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Recent chats */}
      {onSelectConversation && (
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', marginTop: 8 }}>
          <div style={{ padding: '8px 20px 4px', fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Recent Chats
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '0 8px' }}>
            <ConversationList
              activeId={activeConversationId ?? null}
              onSelect={onSelectConversation}
              onNew={onNewConversation ?? (() => {})}
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ padding: '12px 12px', borderTop: '1px solid var(--cr-border)', marginTop: 'auto' }}>
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, padding: '0 8px' }}>
            {user.avatar_url ? (
              <img src={user.avatar_url} alt="" style={{ width: 28, height: 28, borderRadius: '50%' }} />
            ) : (
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  background: 'var(--cr-green-600)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 12,
                  fontWeight: 600,
                }}
              >
                {(user.name || user.email)?.[0]?.toUpperCase() ?? 'U'}
              </div>
            )}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--cr-text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user.name || user.email}
              </div>
            </div>
          </div>
        )}
        <div style={{ display: 'flex', gap: 4 }}>
          <button
            onClick={() => navigate('/settings')}
            style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              padding: '8px', borderRadius: 'var(--cr-radius-xs)', border: 'none',
              background: 'transparent', color: 'var(--cr-text-muted)', cursor: 'pointer', fontSize: 12,
            }}
          >
            <Settings size={14} />
          </button>
          <button
            onClick={logout}
            style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              padding: '8px', borderRadius: 'var(--cr-radius-xs)', border: 'none',
              background: 'transparent', color: 'var(--cr-text-muted)', cursor: 'pointer', fontSize: 12,
            }}
          >
            <LogOut size={14} />
            Sign Out
          </button>
        </div>
      </div>
    </aside>
  );
}

