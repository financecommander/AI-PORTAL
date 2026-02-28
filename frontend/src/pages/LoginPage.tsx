import { useState, type FormEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, AlertCircle } from 'lucide-react';

/** Inline SVG icons for OAuth providers (no extra deps required). */
function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.64 9.2045c0-.638-.0573-1.2518-.1636-1.8409H9v3.4814h4.8436c-.2086 1.125-.8427 2.0782-1.7959 2.7164v2.2581h2.908c1.7018-1.567 2.6836-3.874 2.6836-6.6154z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.4673-.806 5.9564-2.1805l-2.908-2.2581c-.8055.54-1.8368.859-3.0482.859-2.3446 0-4.3282-1.5836-5.036-3.7109H.9574v2.3318C2.4382 15.9832 5.4818 18 9 18z" fill="#34A853"/>
      <path d="M3.964 10.71A5.41 5.41 0 0 1 3.6818 9c0-.5959.1023-1.175.2823-1.71V4.9582H.9573A8.9961 8.9961 0 0 0 0 9c0 1.4523.3477 2.8268.9573 4.0418L3.964 10.71z" fill="#FBBC05"/>
      <path d="M9 3.5795c1.3214 0 2.5077.4541 3.4405 1.346l2.5813-2.5814C13.4632.8918 11.426 0 9 0 5.4818 0 2.4382 2.0168.9573 4.9582L3.964 7.29C4.6718 5.1627 6.6554 3.5795 9 3.5795z" fill="#EA4335"/>
    </svg>
  );
}

function AppleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 814 1000" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
      <path d="M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1s-85.5-39.5-164-39.5c-76 0-103.7 40.8-165.9 40.8s-105-57.8-155.5-127.4C46 411.8 8 312.7 8 215.4c0-189.3 123.3-289.6 244.8-289.6 65.7 0 120.4 43.6 162.4 43.6 40.2 0 103.1-46.2 176.8-46.2 28.5 0 130.9 2.6 198.3 99.2zm-234-181.5c31.1-36.9 53.1-88.1 53.1-139.3 0-7.1-.6-14.3-1.9-20.1-50.6 1.9-110.8 33.7-147.1 75.8-28.5 32.4-55.1 83.6-55.1 135.5 0 7.8 1.3 15.6 1.9 18.1 3.2.6 8.4 1.3 13.6 1.3 45.4 0 102.5-30.4 135.5-71.3z"/>
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 1200 1227" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
      <path d="M714.163 519.284 1160.89 0h-105.86L667.137 450.887 357.328 0H0l468.492 681.821L0 1226.37h105.866l409.625-476.152 327.181 476.152H1200L714.163 519.284zm-144.838 168.36-47.468-67.894-377.686-540.24h162.604l304.797 435.991 47.468 67.894 396.2 566.721H892.14L569.325 687.644z"/>
    </svg>
  );
}

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, error } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const oauthError = searchParams.get('oauth_error');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try { await login(email); navigate('/'); } catch {} finally { setLoading(false); }
  };

  const handleOAuth = (provider: 'google' | 'apple' | 'x') => {
    window.location.href = `/auth/oauth/${provider}/authorize`;
  };

  const displayError = error ?? (oauthError ? `OAuth sign-in failed: ${oauthError.replace(/_/g, ' ')}` : null);

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
        {displayError && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', borderRadius: 'var(--cr-radius-sm)', background: 'rgba(214, 69, 69, 0.1)', border: '1px solid rgba(214, 69, 69, 0.25)', color: 'var(--cr-danger)', fontSize: '13px', marginBottom: '16px' }}>
            <AlertCircle style={{ width: '16px', height: '16px', flexShrink: 0 }} /><span>{displayError}</span>
          </div>
        )}

        {/* OAuth buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
          <button type="button" onClick={() => handleOAuth('google')}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', width: '100%', padding: '11px 16px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'var(--cr-charcoal-deep)', color: 'var(--cr-text)', fontSize: '14px', cursor: 'pointer', transition: 'border-color 150ms' }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}>
            <GoogleIcon /><span>Continue with Google</span>
          </button>
          <button type="button" onClick={() => handleOAuth('apple')}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', width: '100%', padding: '11px 16px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'var(--cr-charcoal-deep)', color: 'var(--cr-text)', fontSize: '14px', cursor: 'pointer', transition: 'border-color 150ms' }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}>
            <AppleIcon /><span>Continue with Apple</span>
          </button>
          <button type="button" onClick={() => handleOAuth('x')}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', width: '100%', padding: '11px 16px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'var(--cr-charcoal-deep)', color: 'var(--cr-text)', fontSize: '14px', cursor: 'pointer', transition: 'border-color 150ms' }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}>
            <XIcon /><span>Continue with X</span>
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', margin: '20px 0' }}>
          <hr style={{ flex: 1, border: 'none', borderTop: '1px solid var(--cr-border)' }} />
          <span style={{ fontSize: '12px', color: 'var(--cr-text-dim)' }}>or sign in with email</span>
          <hr style={{ flex: 1, border: 'none', borderTop: '1px solid var(--cr-border)' }} />
        </div>

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
