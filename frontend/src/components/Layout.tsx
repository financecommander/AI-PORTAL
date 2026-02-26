import { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Menu, X } from 'lucide-react';
import Sidebar from './Sidebar';

export default function Layout() {
  const { isAuthenticated, isLoading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--navy-dark)' }}>
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen" style={{ background: 'var(--navy-dark)' }}>
      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 flex items-center px-4 py-3"
        style={{ background: 'var(--navy)', borderBottom: '1px solid #2A3A5C' }}>
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-white p-1">
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <h1 className="text-lime-400 font-bold ml-3 text-sm">CALCULUS LABS</h1>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="md:hidden fixed inset-0 bg-black/50 z-40" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar — hidden on mobile unless toggled */}
      <div className={`
        fixed left-0 top-0 h-screen z-50 transition-transform duration-200
        md:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <Sidebar onNavigate={() => setSidebarOpen(false)} />
      </div>

      {/* Main content */}
      <main className="min-h-screen md:ml-[var(--sidebar-width)] pt-14 md:pt-0">
        <Outlet />
      </main>
    </div>
  );
}
