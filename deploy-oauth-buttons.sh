#!/bin/bash
set -e
cd /workspaces/AI-PORTAL 2>/dev/null || cd ~/AI-PORTAL 2>/dev/null || { echo "❌"; exit 1; }
mkdir -p 'frontend/src/pages'
cat > 'frontend/src/pages/LoginPage.tsx' << 'FILEEOF_LoginPage'
import { useState } from 'react';
import { Shield, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login, loginWithOAuth } = useAuth();
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

        {/* Divider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '20px 0' }}>
          <div style={{ flex: 1, height: 1, background: 'var(--cr-border)' }} />
          <span style={{ fontSize: 11, color: 'var(--cr-text-muted)' }}>or continue with</span>
          <div style={{ flex: 1, height: 1, background: 'var(--cr-border)' }} />
        </div>

        {/* OAuth buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <button
            onClick={() => loginWithOAuth('google')}
            style={{
              width: '100%', padding: '11px', borderRadius: 'var(--cr-radius-sm)',
              border: '1px solid var(--cr-border)', background: 'var(--cr-white)',
              color: 'var(--cr-text)', fontSize: 13, fontWeight: 500, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              transition: 'border-color 150ms',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
            Continue with Google
          </button>
          <button
            onClick={() => loginWithOAuth('apple')}
            style={{
              width: '100%', padding: '11px', borderRadius: 'var(--cr-radius-sm)',
              border: '1px solid var(--cr-border)', background: 'var(--cr-white)',
              color: 'var(--cr-text)', fontSize: 13, fontWeight: 500, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              transition: 'border-color 150ms',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
            Continue with Apple
          </button>
          <button
            onClick={() => loginWithOAuth('x')}
            style={{
              width: '100%', padding: '11px', borderRadius: 'var(--cr-radius-sm)',
              border: '1px solid var(--cr-border)', background: 'var(--cr-white)',
              color: 'var(--cr-text)', fontSize: 13, fontWeight: 500, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              transition: 'border-color 150ms',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            Continue with X
          </button>
        </div>

        <p style={{ textAlign: 'center', fontSize: 11, color: 'var(--cr-text-dim)', marginTop: 20 }}>
          Calculus Holdings LLC · Secured with JWT authentication
        </p>
      </div>
    </div>
  );
}

FILEEOF_LoginPage
echo "✅ LoginPage updated"
git add -A
git commit --no-gpg-sign -m "feat: add Google/Apple/X OAuth buttons to login page (light theme)" || echo "Nothing"
git push origin main
echo "✅ Pushed. On VM: cd ~/AI-PORTAL && git fetch origin main && git reset --hard origin/main && sudo docker compose -f docker-compose.v2.yml build --no-cache frontend && sudo docker compose -f docker-compose.v2.yml up -d --force-recreate"
