import { useState, type ReactNode } from 'react';
import { api } from '../api/client';
import { AuthContext } from './authContextDef';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const token = localStorage.getItem('fc_token');
    if (token) api.setToken(token);
    return Boolean(token);
  });
  const [isLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (email: string) => {
    setError(null);
    try {
      const response = await api.post<{ access_token: string }>('/auth/login', { email });
      api.setToken(response.access_token);
      localStorage.setItem('fc_token', response.access_token);
      setIsAuthenticated(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    }
  };

  const logout = () => {
    api.setToken(null);
    localStorage.removeItem('fc_token');
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout, error }}>
      {children}
    </AuthContext.Provider>
  );
}

