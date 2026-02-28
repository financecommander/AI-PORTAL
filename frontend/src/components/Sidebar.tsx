import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Sparkles,
  MessageSquare,
  Brain,
  BarChart3,
  Settings,
  LogOut,
  ChevronRight,
} from 'lucide-react';
import clsx from 'clsx';
import ConversationList from './ConversationList';

const navItems = [
  { to: '/', icon: Sparkles, label: 'Chat' },
  { to: '/specialists', icon: MessageSquare, label: 'Specialists' },
  { to: '/pipelines', icon: Brain, label: 'Intelligence Pipelines' },
  { to: '/usage', icon: BarChart3, label: 'Usage & Costs' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

interface SidebarProps {
  onNavigate?: () => void;
  activeConversationId?: string | null;
  onSelectConversation?: (uuid: string) => void;
  onNewConversation?: () => void;
}

export default function Sidebar({
  onNavigate,
  activeConversationId = null,
  onSelectConversation,
  onNewConversation,
}: SidebarProps) {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const handleLogout = () => {
    logout();
    navigate('/login');
    onNavigate?.();
  };

  return (
    <aside
      className="h-screen flex flex-col"
      style={{
        width: 'var(--sidebar-width)',
        background: 'var(--cr-charcoal)',
        borderRight: '1px solid var(--cr-border)',
      }}
    >
      {/* Brand */}
      <div className="px-5 py-5" style={{ borderBottom: '1px solid var(--cr-border)' }}>
        <h1
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: '16px',
            fontWeight: 700,
            color: 'var(--cr-green-400)',
            letterSpacing: '0.04em',
            margin: 0,
          }}
        >
          CALCULUS LABS
        </h1>
        <p style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '2px' }}>
          AI Portal v2.2
        </p>
      </div>

      {/* Nav */}
      <nav className="py-3 px-3 space-y-1" style={{ borderBottom: '1px solid var(--cr-border)' }}>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={() => onNavigate?.()}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2 text-sm transition-all group',
                isActive ? 'font-medium' : '',
              )
            }
            style={({ isActive }) => ({
              borderRadius: 'var(--cr-radius-sm)',
              background: isActive ? 'var(--cr-charcoal-deep)' : 'transparent',
              color: isActive ? 'var(--cr-green-400)' : 'var(--cr-text-muted)',
              borderLeft: isActive
                ? '2px solid var(--cr-green-600)'
                : '2px solid transparent',
            })}
          >
            <Icon className="w-[18px] h-[18px] shrink-0" />
            <span className="flex-1">{label}</span>
            <ChevronRight
              className="w-4 h-4 opacity-0 group-hover:opacity-40 transition-opacity"
              style={{ color: 'var(--cr-text-dim)' }}
            />
          </NavLink>
        ))}
      </nav>

      {/* Conversation History */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <div
          style={{
            padding: '10px 14px 4px',
            fontSize: '10px',
            fontWeight: 600,
            color: 'var(--cr-text-dim)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
          }}
        >
          Recent chats
        </div>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <ConversationList
            activeId={activeConversationId}
            onSelect={(uuid) => {
              onSelectConversation?.(uuid);
              navigate('/');
              onNavigate?.();
            }}
            onNew={() => {
              onNewConversation?.();
              navigate('/');
              onNavigate?.();
            }}
          />
        </div>
      </div>

      {/* User + Sign Out */}
      <div className="px-3 py-3" style={{ borderTop: '1px solid var(--cr-border)' }}>
        {user && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '4px 8px',
              marginBottom: '6px',
            }}
          >
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt=""
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  border: '1px solid var(--cr-border)',
                }}
              />
            ) : (
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: 'var(--cr-green-900)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--cr-green-400)',
                }}
              >
                {(user.name || user.email).charAt(0).toUpperCase()}
              </div>
            )}
            <span
              style={{
                fontSize: '12px',
                color: 'var(--cr-text-muted)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {user.name || user.email}
            </span>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 text-sm w-full transition-all"
          style={{
            color: 'var(--cr-text-dim)',
            borderRadius: 'var(--cr-radius-sm)',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-danger)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-dim)';
          }}
        >
          <LogOut className="w-[18px] h-[18px]" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}

