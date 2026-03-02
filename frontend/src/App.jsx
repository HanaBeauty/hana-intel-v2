import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Radar from './pages/Radar';
import ReviewBoard from './pages/ReviewBoard';
import ControlTower from './pages/ControlTower';
import StrategyRoom from './pages/StrategyRoom';
import Settings from './pages/Settings';
import NurtureHub from './pages/NurtureHub';

// Auth e IAM
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';

// Mock Componente de Proteção
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-[#0d0905]"><div className="w-8 h-8 rounded-full border-t-2 border-[#d5aa53] animate-spin"></div></div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Componente para limitar perfis de acesso
const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Carregando...</div>;
  }

  if (!user || user.role !== 'ADMIN') {
    return <Navigate to="/dashboard/radar" replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Rotas Públicas */}
          <Route path="/login" element={<Login />} />

          {/* Envelopamento Mestre (IAM) */}
          <Route path="/" element={<Navigate to="/dashboard/radar" replace />} />

          <Route path="/dashboard" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Navigate to="radar" replace />} />

            {/* Rotas Comuns (C-Level e Atendentes) */}
            <Route path="radar" element={<Radar />} />

            {/* Rotas Administrativas (Apenas C-Level) */}
            <Route path="control-tower" element={<AdminRoute><ControlTower /></AdminRoute>} />
            <Route path="review-board" element={<AdminRoute><ReviewBoard /></AdminRoute>} />
            <Route path="strategy-room" element={<AdminRoute><StrategyRoom /></AdminRoute>} />
            <Route path="settings" element={<AdminRoute><Settings /></AdminRoute>} />
            <Route path="nurture-hub" element={<AdminRoute><NurtureHub /></AdminRoute>} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
