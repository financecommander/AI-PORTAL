import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Sparkles, MessageSquare, Brain, BarChart3, Settings, LogOut, ChevronRight } from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { to: '/', icon: Sparkles, label: 'Chat' },
  { to: '/specialists', icon: MessageSquare, label: 'Specialists' },
  { to: '/pipelines', icon: Brain, label: 'Intelligence Pipelines' },
  { to: '/usage', icon: BarChart3, label: 'Usage & Costs' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

interface SidebarProps { onNavigate?: () => void; }

export default function Sidebar({ onNavigate }: SidebarProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const handleLogout = () => { logout(); navigate('/login'); onNavigate?.(); };

  return (
    <aside className="h-screen flex flex-col" style={{ width: 'var(--sidebar-width)', background: 'var(--cr-charcoal)', borderRight: '1px solid var(--cr-border)' }}>
      <div className="px-5 py-5" style={{ borderBottom: '1px solid var(--cr-border)' }}>
        <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: '16px', fontWeight: 700, color: 'var(--cr-green-400)', letterSpacing: '0.04em', margin: 0 }}>CALCULUS LABS</h1>
        <p style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '2px' }}>AI Portal v2.2</p>
      </div>
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} end={to === '/'} onClick={() => onNavigate?.()}
            className={({ isActive }) => clsx('flex items-center gap-3 px-3 py-2.5 text-sm transition-all group', isActive ? 'font-medium' : '')}
            style={({ isActive }) => ({ borderRadius: 'var(--cr-radius-sm)', background: isActive ? 'var(--cr-charcoal-deep)' : 'transparent', color: isActive ? 'var(--cr-green-400)' : 'var(--cr-text-muted)', borderLeft: isActive ? '2px solid var(--cr-green-600)' : '2px solid transparent' })}>
            <Icon className="w-[18px] h-[18px] shrink-0" />
            <span className="flex-1">{label}</span>
            <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-40 transition-opacity" style={{ color: 'var(--cr-text-dim)' }} />
          </NavLink>
        ))}
      </nav>
      <div className="px-3 py-4" style={{ borderTop: '1px solid var(--cr-border)' }}>
        <button onClick={handleLogout} className="flex items-center gap-3 px-3 py-2.5 text-sm w-full transition-all" style={{ color: 'var(--cr-text-dim)', borderRadius: 'var(--cr-radius-sm)', background: 'transparent', border: 'none', cursor: 'pointer' }}
          onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-danger)'; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-dim)'; }}>
          <LogOut className="w-[18px] h-[18px]" /><span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
