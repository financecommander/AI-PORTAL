import { useState, useContext } from 'react';
import { Shield, AlertCircle } from 'lucide-react';
import { AuthContext } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email.trim()) return;
    setLoading(true);
    setError('');
    try {
      await login(email.trim());
    } catch (err: any) {
      setError(err?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--cr-surface)',
        padding: 24,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 400,
          background: 'var(--cr-white)',
          borderRadius: 'var(--cr-radius)',
          border: '1px solid var(--cr-border)',
          padding: '48px 40px',
        }}
      >
        {/* Brand */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: 12,
              background: 'var(--cr-green-900)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16,
            }}
          >
            <Shield style={{ width: 24, height: 24, color: '#FFFFFF' }} />
          </div>
          <h1
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: 22,
              fontWeight: 700,
              color: 'var(--cr-text)',
              margin: '0 0 4px',
              letterSpacing: '-0.02em',
            }}
          >
            Calculus Research
          </h1>
          <p style={{ fontSize: 13, color: 'var(--cr-text-muted)', margin: 0 }}>
            AI Intelligence Portal v2.2
          </p>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 14px',
              background: '#FEF2F2',
              border: '1px solid #FECACA',
              borderRadius: 'var(--cr-radius-sm)',
              marginBottom: 16,
              color: 'var(--cr-danger)',
              fontSize: 13,
            }}
          >
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {/* Email field */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--cr-text-secondary)', marginBottom: 6 }}>
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder="finance@calculusresearch.io"
            style={{
              width: '100%',
              padding: '12px 14px',
              borderRadius: 'var(--cr-radius-sm)',
              border: '1px solid var(--cr-border)',
              background: 'var(--cr-white)',
              color: 'var(--cr-text)',
              fontSize: 14,
              outline: 'none',
              transition: 'border-color 150ms',
            }}
            onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}
          />
          <p style={{ fontSize: 11, color: 'var(--cr-text-muted)', marginTop: 4 }}>
            Domain-restricted access: @calculusresearch.io
          </p>
        </div>

        {/* Sign in button */}
        <button
          onClick={handleSubmit}
          disabled={loading || !email.trim()}
          style={{
            width: '100%',
            padding: '12px',
            borderRadius: 'var(--cr-radius-sm)',
            border: 'none',
            background: 'var(--cr-green-900)',
            color: '#FFFFFF',
            fontSize: 14,
            fontWeight: 600,
            cursor: loading ? 'wait' : 'pointer',
            opacity: loading || !email.trim() ? 0.6 : 1,
            transition: 'opacity 150ms',
          }}
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>

        <p style={{ textAlign: 'center', fontSize: 11, color: 'var(--cr-text-dim)', marginTop: 20 }}>
          Calculus Holdings LLC · Secured with JWT authentication
        </p>
      </div>
    </div>
  );
}

