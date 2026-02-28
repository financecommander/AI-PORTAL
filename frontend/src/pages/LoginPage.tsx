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
    try { await login(email); navigate('/'); } catch {} finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--cr-charcoal-dark)' }}>
      <div style={{ width: '100%', maxWidth: '420px', padding: '40px 36px', background: 'var(--cr-charcoal)', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius)' }}>
        <div style={{ textAlign: 'center', marginBottom: '36px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '56px', height: '56px', borderRadius: '14px', background: 'var(--cr-green-900)', border: '1px solid var(--cr-green-700)', marginBottom: '16px' }}>
            <Shield style={{ width: '28px', height: '28px', color: 'var(--cr-green-400)' }} />
          </div>
          <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: '22px', fontWeight: 700, color: 'var(--cr-green-400)', letterSpacing: '0.04em', margin: '0 0 4px' }}>CALCULUS LABS</h1>
          <p style={{ fontSize: '12px', color: 'var(--cr-text-dim)', margin: 0 }}>AI Intelligence Portal v2.2</p>
        </div>
        {error && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', borderRadius: 'var(--cr-radius-sm)', background: 'rgba(214, 69, 69, 0.1)', border: '1px solid rgba(214, 69, 69, 0.25)', color: 'var(--cr-danger)', fontSize: '13px', marginBottom: '16px' }}>
            <AlertCircle style={{ width: '16px', height: '16px', flexShrink: 0 }} /><span>{error}</span>
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, color: 'var(--cr-text-muted)', marginBottom: '8px' }}>Email Address</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@calculusresearch.io" required
            style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'var(--cr-charcoal-deep)', color: 'var(--cr-text)', fontSize: '14px', outline: 'none', transition: 'border-color 150ms' }}
            onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }} />
          <p style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '6px' }}>Domain-restricted access: @calculusresearch.io</p>
          <button type="submit" disabled={loading || !email}
            style={{ width: '100%', marginTop: '24px', padding: '12px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-green-700)', background: 'var(--cr-green-900)', color: 'var(--cr-green-400)', fontFamily: "'Space Grotesk', sans-serif", fontSize: '14px', fontWeight: 600, cursor: loading || !email ? 'not-allowed' : 'pointer', opacity: loading || !email ? 0.5 : 1, transition: 'all 150ms' }}>
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>
        <p style={{ textAlign: 'center', fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '28px' }}>Calculus Holdings LLC &middot; Secured with JWT authentication</p>
      </div>
    </div>
  );
}
