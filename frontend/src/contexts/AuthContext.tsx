import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { api } from '../api/client';

interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar_url: string;
  provider: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  login: (email: string) => Promise<void>;
  loginWithOAuth: (provider: 'google' | 'apple' | 'x') => Promise<void>;
  handleOAuthCallback: (provider: string, code: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('fc_token');
    if (token) {
      api.setToken(token);
      // Load user profile
      api.request<UserProfile>('/auth/me')
        .then((profile) => {
          setUser(profile);
          setIsAuthenticated(true);
        })
        .catch(() => {
          // Token expired or invalid
          localStorage.removeItem('fc_token');
          api.setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }

    // Check for OAuth callback params in URL
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');  // contains provider
    if (code && state) {
      handleOAuthCallback(state, code).then(() => {
        // Clean URL
        window.history.replaceState({}, '', window.location.pathname);
      });
    }
  }, []);

  const _setAuth = (token: string) => {
    api.setToken(token);
    localStorage.setItem('fc_token', token);
    setIsAuthenticated(true);
  };

  const login = async (email: string) => {
    setError(null);
    try {
      const response = await api.post<{ access_token: string }>('/auth/login', { email });
      _setAuth(response.access_token);
      // Load profile
      const profile = await api.request<UserProfile>('/auth/me');
      setUser(profile);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    }
  };

  const loginWithOAuth = async (provider: 'google' | 'apple' | 'x') => {
    setError(null);
    try {
      const response = await api.request<{ auth_url: string }>(`/auth/${provider}`);
      // Redirect to OAuth provider
      window.location.href = response.auth_url;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'OAuth redirect failed';
      setError(message);
      throw err;
    }
  };

  const handleOAuthCallback = async (provider: string, code: string) => {
    setError(null);
    try {
      const response = await api.post<{ access_token: string }>(
        `/auth/${provider}/callback`,
        { code },
      );
      _setAuth(response.access_token);
      const profile = await api.request<UserProfile>('/auth/me');
      setUser(profile);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'OAuth login failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.setToken(null);
    localStorage.removeItem('fc_token');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, isLoading, user, login, loginWithOAuth, handleOAuthCallback, logout, error }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

