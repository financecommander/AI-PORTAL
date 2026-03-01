import { useState } from 'react';
import { Outlet, Navigate, useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Menu, X } from 'lucide-react';
import Sidebar from './Sidebar';

export default function Layout() {
  const { isAuthenticated, isLoading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--cr-surface)' }}>
      <div style={{ color: 'var(--cr-text-muted)', fontSize: 14 }}>Loading...</div>
    </div>
  );

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  // Active conversation from URL: /?c=<uuid>
  const activeConversationId = location.pathname === '/' ? searchParams.get('c') : null;

  const handleSelectConversation = (uuid: string) => {
    navigate(`/?c=${uuid}`);
    setSidebarOpen(false);
  };

  const handleNewConversation = () => {
    navigate('/');
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen" style={{ background: 'var(--cr-surface)' }}>
      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 flex items-center px-4 py-3" style={{ background: 'var(--cr-white)', borderBottom: '1px solid var(--cr-border)' }}>
        <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ color: 'var(--cr-text)' }} className="p-1">
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <div className="ml-3 flex items-center gap-2">
          <div style={{ width: 24, height: 24, borderRadius: 6, background: 'var(--cr-green-900)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 11, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>C</div>
          <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 14, fontWeight: 600, color: 'var(--cr-text)' }}>Calculus Research</span>
        </div>
      </div>
      {/* Mobile overlay */}
      {sidebarOpen && <div className="md:hidden fixed inset-0 z-40" style={{ background: 'rgba(0,0,0,0.3)' }} onClick={() => setSidebarOpen(false)} />}
      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-screen z-50 transition-transform duration-200 md:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <Sidebar
          activeConversationId={activeConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onNavigate={() => setSidebarOpen(false)}
        />
      </div>
      {/* Main content */}
      <main className="min-h-screen md:ml-[var(--sidebar-width)] pt-14 md:pt-0"><Outlet /></main>
    </div>
  );
}

