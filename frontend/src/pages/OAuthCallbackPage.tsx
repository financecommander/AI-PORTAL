import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Handles the post-OAuth redirect from the backend.
 * The backend redirects here with ?token=<jwt> after a successful OAuth flow.
 * We store the token and send the user to the main app.
 */
export default function OAuthCallbackPage() {
  const navigate = useNavigate();
  const { handleOAuthToken } = useAuth();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const error = params.get('error');

    if (error) {
      navigate(`/login?oauth_error=${encodeURIComponent(error)}`, { replace: true });
      return;
    }

    if (token) {
      handleOAuthToken(token);
      navigate('/', { replace: true });
    } else {
      navigate('/login?oauth_error=missing_token', { replace: true });
    }
  }, [navigate, handleOAuthToken]);

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--cr-charcoal-dark)',
        color: 'var(--cr-text-muted)',
        fontSize: '14px',
      }}
    >
      Completing sign-in…
    </div>
  );
}
