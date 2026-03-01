import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
    return (
        <div className="layout">
            <Sidebar />
            <main className="main-content">
                <div className="content-container">
                    <Outlet />
                </div>
            </main>

            <style>{`
        .layout {
          display: flex;
          min-height: 100vh;
        }

        .main-content {
          flex: 1;
          margin-left: 260px; /* Width of Sidebar */
          min-height: 100vh;
          background: var(--color-bg-base);
          position: relative;
        }

        /* Ambient glow effect */
        .main-content::before {
          content: '';
          position: absolute;
          top: -200px;
          right: -200px;
          width: 500px;
          height: 500px;
          background: radial-gradient(circle, var(--color-primary-light) 0%, transparent 70%);
          pointer-events: none;
          z-index: 0;
        }

        .content-container {
          position: relative;
          z-index: 10;
          padding: 40px;
          max-width: 1400px;
          margin: 0 auto;
        }
      `}</style>
        </div>
    );
}
