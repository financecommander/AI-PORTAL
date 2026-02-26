import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email);
      navigate('/');
    } catch {
      // error is set in context
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--navy-dark)' }}>
      <div className="w-full max-w-md p-8 rounded-2xl shadow-2xl" style={{ background: 'var(--navy)' }}>
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
               style={{ background: 'var(--blue)', opacity: 0.9 }}>
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-lime-400">CALCULUS LABS</h1>
          <p className="text-sm mt-1" style={{ color: '#8899AA' }}>AI Intelligence Portal v2.0</p>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg mb-4 text-sm"
               style={{ background: 'rgba(192, 57, 43, 0.15)', color: '#E74C3C' }}>
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <label className="block text-sm font-medium mb-2" style={{ color: '#8899AA' }}>
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@financecommander.com"
            required
            className="w-full px-4 py-3 rounded-lg text-white text-sm outline-none transition-all
                       focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
            style={{ background: 'var(--navy-dark)', border: '1px solid #2A3A5C' }}
          />
          <p className="text-xs mt-2" style={{ color: '#667788' }}>
            Domain-restricted access: @financecommander.com only
          </p>

          <button
            type="submit"
            disabled={loading || !email}
            className="w-full mt-6 py-3 rounded-lg text-white font-semibold text-sm transition-all
                       disabled:opacity-50 disabled:cursor-not-allowed hover:brightness-110"
            style={{ background: 'var(--blue)' }}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* Footer */}
        <p className="text-center text-xs mt-6" style={{ color: '#556677' }}>
          Calculus Holdings LLC &middot; Secured with JWT authentication
        </p>
      </div>
    </div>
  );
}
