import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import LLMChatPage from './pages/LLMChatPage';
import ChatPage from './pages/ChatPage';
import PipelinesPage from './pages/PipelinesPage';
import UsagePage from './pages/UsagePage';
import SettingsPage from './pages/SettingsPage';

function LoginGuard() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (isAuthenticated) return <Navigate to="/" replace />;
  return <LoginPage />;
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginGuard />} />
            <Route element={<Layout />}>
              <Route index element={<LLMChatPage />} />
              <Route path="specialists" element={<ChatPage />} />
              <Route path="pipelines" element={<PipelinesPage />} />
              <Route path="usage" element={<UsagePage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
