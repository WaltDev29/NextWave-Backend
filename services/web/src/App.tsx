import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './stores/authStore';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import TeamPage from './pages/TeamPage';
import ProfilePage from './pages/ProfilePage';
import Header from './components/layout/Header';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/auth" replace />;
  return (
    <>
      <Header />
      <main style={{ flex: 1, overflowY: 'auto' }}>{children}</main>
    </>
  );
}

export default function App() {
  console.log('App component is rendering...');
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/" element={
            <ProtectedLayout><DashboardPage /></ProtectedLayout>
          } />
          <Route path="/teams/:teamId" element={
            <ProtectedLayout><TeamPage /></ProtectedLayout>
          } />
          <Route path="/profile" element={
            <ProtectedLayout><ProfilePage /></ProtectedLayout>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
