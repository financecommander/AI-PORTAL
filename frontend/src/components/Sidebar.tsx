import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Sparkles, MessageSquare, Brain, BarChart3, Settings, LogOut, ChevronRight
} from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { to: '/', icon: Sparkles, label: 'Chat' },
  { to: '/specialists', icon: MessageSquare, label: 'Specialists' },
  { to: '/pipelines', icon: Brain, label: 'Intelligence Pipelines' },
  { to: '/usage', icon: BarChart3, label: 'Usage & Costs' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

interface SidebarProps {
  onNavigate?: () => void;
}

export default function Sidebar({ onNavigate }: SidebarProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
    onNavigate?.();
  };

  return (
    <aside
      className="h-screen flex flex-col"
      style={{ width: 'var(--sidebar-width)', background: 'var(--navy)' }}
    >
      <div className="px-5 py-5 border-b" style={{ borderColor: '#2A3A5C' }}>
        <h1 className="text-lg font-bold text-lime-400 tracking-tight">CALCULUS LABS</h1>
        <p className="text-xs mt-0.5" style={{ color: '#667788' }}>AI Portal v2.0</p>
      </div>

      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={() => onNavigate?.()}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all group',
              isActive ? 'text-white font-medium' : 'hover:text-white'
            )}
            style={({ isActive }) => ({
              background: isActive ? 'var(--navy-light)' : 'transparent',
              color: isActive ? '#FFFFFF' : '#8899AA',
            })}
          >
            <Icon className="w-5 h-5 shrink-0" />
            <span className="flex-1">{label}</span>
            <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-50 transition-opacity" />
          </NavLink>
        ))}
      </nav>

      <div className="px-3 py-4 border-t" style={{ borderColor: '#2A3A5C' }}>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm w-full transition-all hover:text-white"
          style={{ color: '#8899AA' }}
        >
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
