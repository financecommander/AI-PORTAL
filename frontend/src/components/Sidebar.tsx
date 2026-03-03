
import { useLocation, useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Bot,
  Layers,
  Boxes,
  BarChart3,
  LogOut,
  Settings,
  Monitor,
  Sun,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../hooks/useTheme';
import ConversationList from './ConversationList';

interface SidebarProps {
  activeConversationId?: string | null;
  onSelectConversation?: (id: string) => void;
  onNewConversation?: () => void;
  onNavigate?: () => void;
}

const NAV_ITEMS = [
  { label: 'Console', icon: MessageSquare, path: '/' },
  { label: 'Analyst Desks', icon: Bot, path: '/specialists' },
  { label: 'Engines', icon: Layers, path: '/pipelines' },
  { label: 'Swarm Mainframe', icon: Boxes, path: '/swarm' },
  { label: 'Metrics', icon: BarChart3, path: '/usage' },
];

export default function Sidebar({
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onNavigate,
}: SidebarProps) {
  const { user, logout } = useAuth();
  const { theme, toggle: toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--cr-panel)',
        borderRight: '1px solid var(--cr-border)',
        flexShrink: 0,
      }}
    >
      {/* Brand */}
      <div style={{ padding: '20px 20px 16px' }}>
        <a
          href="http://34.26.53.11"
          target="_blank"
          rel="noopener noreferrer"
          style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}
        >
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
        </a>
      </div>

      {/* Navigation */}
      <nav style={{ padding: '0 12px' }}>
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <button
              key={item.path}
              className="sidebar-nav-item"
              onClick={() => { navigate(item.path); onNavigate?.(); }}
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
            onClick={toggleTheme}
            title={theme === 'light' ? 'Terminal Mode' : 'Light Mode'}
            style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              padding: '8px', borderRadius: 'var(--cr-radius-xs)', border: 'none',
              background: 'transparent', color: 'var(--cr-text-muted)', cursor: 'pointer', fontSize: 12,
            }}
          >
            {theme === 'light' ? <Monitor size={14} /> : <Sun size={14} />}
          </button>
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

