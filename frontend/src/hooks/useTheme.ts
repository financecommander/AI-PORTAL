import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'cr_theme';
type Theme = 'light' | 'terminal';

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'terminal' ? 'terminal' : 'light';
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'terminal') {
      root.classList.add('terminal');
    } else {
      root.classList.remove('terminal');
    }
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const toggle = useCallback(() => {
    setThemeState((prev) => (prev === 'light' ? 'terminal' : 'light'));
  }, []);

  return { theme, toggle, isTerminal: theme === 'terminal' };
}
