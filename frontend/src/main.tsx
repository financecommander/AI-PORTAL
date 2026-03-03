import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

// Apply saved theme immediately to prevent flash
if (localStorage.getItem('cr_theme') === 'terminal') {
  document.documentElement.classList.add('terminal');
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
