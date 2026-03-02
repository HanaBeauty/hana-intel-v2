import { NavLink } from 'react-router-dom';
import { Activity, MailCheck, Settings, Home, BrainCircuit, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Sidebar() {
  const { user, logout } = useAuth();

  const allRoutes = [
    { path: '/dashboard/control-tower', label: 'Torre de Controle', icon: <Activity size={20} />, requiresAdmin: true },
    { path: '/dashboard/radar', label: 'Radar 360', icon: <Activity size={20} />, requiresAdmin: false },
    { path: '/dashboard/review-board', label: 'Aprovador (CRM)', icon: <MailCheck size={20} />, requiresAdmin: true },
    { path: '/dashboard/nurture-hub', label: 'Nurture Hub', icon: <BrainCircuit size={20} />, requiresAdmin: true },
    { path: '/dashboard/strategy-room', label: 'Strategy Room', icon: <Home size={20} />, requiresAdmin: true },
    { path: '/dashboard/settings', label: 'Configurações', icon: <Settings size={20} />, requiresAdmin: true }
  ];

  // Filtra as rotas se for ATENDENTE (Remove tudo que exige admin)
  const routes = allRoutes.filter(route => {
    if (route.requiresAdmin && user?.role !== 'ADMIN') return false;
    return true;
  });

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="brand-title">HANA INTEL <span className="version">2.0</span></h2>
      </div>

      <nav className="sidebar-nav">
        {routes.map((route, i) => (
          <NavLink
            key={i}
            to={route.path !== '#' ? route.path : '/#'}
            className={({ isActive }) => `nav-item ${isActive && route.path !== '#' ? 'active' : ''}`}
          >
            <span className="nav-icon">{route.icon}</span>
            <span className="nav-label">{route.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="avatar">{user?.name ? user.name.substring(0, 2).toUpperCase() : 'UI'}</div>
          <div className="user-info">
            <p className="user-name">{user?.name || 'Carregando...'}</p>
            <p className="user-role">{user?.role === 'ADMIN' ? 'CEO / Master Admin' : 'Atendente Elite'}</p>
          </div>
          <div className="logout-button ml-auto mr-[-5px]">
            <button onClick={logout} className="text-[#a49174] hover:text-[#d5aa53] transition-colors p-2" title="Desconectar">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </div>

      <style>{`
        .sidebar {
          width: 260px;
          height: 100vh;
          background: var(--color-bg-surface);
          border-right: 1px solid var(--color-border);
          display: flex;
          flex-direction: column;
          position: fixed;
          left: 0;
          top: 0;
          z-index: 50;
        }

        .sidebar-header {
          padding: 32px 24px;
        }

        .brand-title {
          font-size: 1.125rem;
          font-weight: 700;
          color: var(--color-primary);
          letter-spacing: 0.1em;
        }

        .version {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
          background: var(--color-bg-surface-elevated);
          padding: 2px 6px;
          border-radius: 4px;
          margin-left: 8px;
        }

        .sidebar-nav {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
          padding: 0 16px;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-radius: 8px;
          color: var(--color-text-secondary);
          transition: all 0.2s;
        }

        .nav-item:hover {
          color: var(--color-text-primary);
          background: rgba(255, 255, 255, 0.03);
        }

        .nav-item.active {
          color: var(--color-primary);
          background: var(--color-primary-light);
        }

        .sidebar-footer {
          padding: 24px;
          border-top: 1px solid var(--color-border);
        }

        .user-profile {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: var(--color-primary);
          color: #000;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 0.875rem;
        }

        .user-name {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text-primary);
        }

        .user-role {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
        }
      `}</style>
    </aside>
  );
}
