import { useContext } from 'react';
import { AuthContext } from '../contexts/authContextDef';
import type { AuthContextType } from '../contexts/authContextDef';

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
