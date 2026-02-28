import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, AlertCircle, Mail } from 'lucide-react';

/* ── Social icon SVGs (inline to avoid deps) ─────────────────── */

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  );
}

function AppleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

/* ── Component ───────────────────────────────────────────────── */

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [showEmail, setShowEmail] = useState(false);
  const { login, loginWithOAuth, error } = useAuth();
  const navigate = useNavigate();

  const handleEmailSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email);
      navigate('/');
    } catch {
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = async (provider: 'google' | 'apple' | 'x') => {
    setLoading(true);
    try {
      await loginWithOAuth(provider);
      // OAuth redirects to provider — page will reload on callback
    } catch {
      setLoading(false);
    }
  };

  const btnBase: React.CSSProperties = {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
    padding: '12px',
    borderRadius: 'var(--cr-radius-sm)',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 150ms',
    border: 'none',
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{ background: 'var(--cr-charcoal-dark)' }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '420px',
          padding: '40px 36px',
          background: 'var(--cr-charcoal)',
          border: '1px solid var(--cr-border)',
          borderRadius: 'var(--cr-radius)',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '56px',
              height: '56px',
              borderRadius: '14px',
              background: 'var(--cr-green-900)',
              border: '1px solid var(--cr-green-700)',
              marginBottom: '16px',
            }}
          >
            <Shield style={{ width: '28px', height: '28px', color: 'var(--cr-green-400)' }} />
          </div>
          <h1
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: '22px',
              fontWeight: 700,
              color: 'var(--cr-green-400)',
              letterSpacing: '0.04em',
              margin: '0 0 4px',
            }}
          >
            CALCULUS LABS
          </h1>
          <p style={{ fontSize: '12px', color: 'var(--cr-text-dim)', margin: 0 }}>
            AI Intelligence Portal v2.2
          </p>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 14px',
              borderRadius: 'var(--cr-radius-sm)',
              background: 'rgba(214, 69, 69, 0.1)',
              border: '1px solid rgba(214, 69, 69, 0.25)',
              color: 'var(--cr-danger)',
              fontSize: '13px',
              marginBottom: '16px',
            }}
          >
            <AlertCircle style={{ width: '16px', height: '16px', flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* OAuth Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
          <button
            onClick={() => handleOAuth('google')}
            disabled={loading}
            style={{
              ...btnBase,
              background: '#ffffff',
              color: '#1f1f1f',
            }}
          >
            <GoogleIcon />
            Continue with Google
          </button>

          <button
            onClick={() => handleOAuth('apple')}
            disabled={loading}
            style={{
              ...btnBase,
              background: '#000000',
              color: '#ffffff',
            }}
          >
            <AppleIcon />
            Continue with Apple
          </button>

          <button
            onClick={() => handleOAuth('x')}
            disabled={loading}
            style={{
              ...btnBase,
              background: '#14171a',
              color: '#ffffff',
            }}
          >
            <XIcon />
            Continue with X
          </button>
        </div>

        {/* Divider */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            margin: '20px 0',
          }}
        >
          <div style={{ flex: 1, height: '1px', background: 'var(--cr-border)' }} />
          <span style={{ fontSize: '11px', color: 'var(--cr-text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            or
          </span>
          <div style={{ flex: 1, height: '1px', background: 'var(--cr-border)' }} />
        </div>

        {/* Email Login */}
        {!showEmail ? (
          <button
            onClick={() => setShowEmail(true)}
            style={{
              ...btnBase,
              background: 'transparent',
              color: 'var(--cr-text-muted)',
              border: '1px solid var(--cr-border)',
            }}
          >
            <Mail style={{ width: 16, height: 16 }} />
            Continue with email
          </button>
        ) : (
          <form onSubmit={handleEmailSubmit}>
            <label
              style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: 500,
                color: 'var(--cr-text-muted)',
                marginBottom: '8px',
              }}
            >
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@calculusresearch.io"
              required
              autoFocus
              style={{
                width: '100%',
                padding: '12px 16px',
                borderRadius: 'var(--cr-radius-sm)',
                border: '1px solid var(--cr-border)',
                background: 'var(--cr-charcoal-deep)',
                color: 'var(--cr-text)',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 150ms',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'var(--cr-green-600)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'var(--cr-border)';
              }}
            />
            <p style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '6px' }}>
              Domain-restricted: @calculusresearch.io or @gradeesolutions.com
            </p>
            <button
              type="submit"
              disabled={loading || !email}
              style={{
                ...btnBase,
                marginTop: '16px',
                background: 'var(--cr-green-900)',
                color: 'var(--cr-green-400)',
                border: '1px solid var(--cr-green-700)',
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 600,
                opacity: loading || !email ? 0.5 : 1,
                cursor: loading || !email ? 'not-allowed' : 'pointer',
              }}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        )}

        <p
          style={{
            textAlign: 'center',
            fontSize: '11px',
            color: 'var(--cr-text-dim)',
            marginTop: '28px',
          }}
        >
          Calculus Holdings LLC &middot; Secured with JWT authentication
        </p>
      </div>
    </div>
  );
}

