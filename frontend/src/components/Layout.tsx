import { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Menu, X } from 'lucide-react';
import Sidebar from './Sidebar';

export default function Layout() {
  const { isAuthenticated, isLoading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--cr-charcoal-dark)' }}>
      <div style={{ color: 'var(--cr-text-muted)', fontSize: '14px' }}>Loading...</div>
    </div>
  );

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen" style={{ background: 'var(--cr-charcoal-dark)' }}>
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 flex items-center px-4 py-3" style={{ background: 'var(--cr-charcoal)', borderBottom: '1px solid var(--cr-border)' }}>
        <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ color: 'var(--cr-text)' }} className="p-1">
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <h1 className="ml-3" style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: '14px', fontWeight: 700, color: 'var(--cr-green-400)', letterSpacing: '0.04em' }}>CALCULUS LABS</h1>
      </div>
      {sidebarOpen && <div className="md:hidden fixed inset-0 z-40" style={{ background: 'rgba(14, 16, 18, 0.7)' }} onClick={() => setSidebarOpen(false)} />}
      <div className={`fixed left-0 top-0 h-screen z-50 transition-transform duration-200 md:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <Sidebar onNavigate={() => setSidebarOpen(false)} />
      </div>
      <main className="min-h-screen md:ml-[var(--sidebar-width)] pt-14 md:pt-0"><Outlet /></main>
    </div>
  );
}
