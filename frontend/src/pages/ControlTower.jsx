import { useState, useEffect } from 'react';
import { Activity, MailCheck, MessageCircle, AlertCircle, RefreshCw, StopCircle } from 'lucide-react';

export default function ControlTower() {
    const [metrics, setMetrics] = useState({
        health: { redis: 'offline', db: 'offline', whatsapp: 'offline' },
        performance: { messages_today: 0, campaigns_active: 0, bounces: 0 },
        crm: { active_leads: 0, ltv: 'Calculando...' },
        logs: []
    });

    const [isLoading, setIsLoading] = useState(true);

    const fetchTelemetry = async () => {
        try {
            setIsLoading(true);
            const res = await fetch('/api/v1/dashboard/telemetry');
            if (res.ok) {
                const data = await res.json();
                setMetrics(data);
            }
        } catch (err) {
            console.error('Erro ao buscar telemetria:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchTelemetry();
        // Refresh a cada 30 segundos
        const interval = setInterval(fetchTelemetry, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="control-tower animate-fade-in">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Torre de Controle</h1>
                    <p className="page-subtitle">Visão geral do ecossistema inteligente V2.0.</p>
                </div>
            </header>

            <div className="metrics-grid">
                {/* Saúde dos Sistemas */}
                <div className="metric-card glass-panel">
                    <div className="metric-header">
                        <Activity className="text-success" size={24} />
                        <h3>Saúde dos Sistemas</h3>
                    </div>
                    <div className="system-status-list">
                        <div className="status-row">
                            <span>Banco de Dados (Vector/PG)</span>
                            <span className={`status-dot ${metrics.health.db}`}></span>
                        </div>
                        <div className="status-row">
                            <span>Memória L1 (Redis)</span>
                            <span className={`status-dot ${metrics.health.redis}`}></span>
                        </div>
                        <div className="status-row">
                            <span>Evolution API (WhatsApp)</span>
                            <span className={`status-dot ${metrics.health.whatsapp}`}></span>
                        </div>
                    </div>
                </div>

                {/* Performance Hoje */}
                <div className="metric-card glass-panel">
                    <div className="metric-header">
                        <MailCheck className="text-primary" size={24} />
                        <h3>Performance Hoje</h3>
                    </div>
                    <div className="stats-list">
                        <div className="stat-item">
                            <span className="stat-value">{metrics.performance.messages_today}</span>
                            <span className="stat-label">Mensagens Processadas</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value text-danger">{metrics.performance.bounces}</span>
                            <span className="stat-label">Bounces/Falhas</span>
                        </div>
                    </div>
                </div>

                {/* Inteligência CRM */}
                <div className="metric-card glass-panel">
                    <div className="metric-header">
                        <MessageCircle className="text-warning" size={24} />
                        <h3>Inteligência CRM</h3>
                    </div>
                    <div className="stats-list">
                        <div className="stat-item">
                            <span className="stat-value text-warning">{metrics.crm.active_leads}</span>
                            <span className="stat-label">Leads Mapeados</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value text-success">{metrics.crm.ltv}</span>
                            <span className="stat-label">LTV Acumulado Estimado</span>
                        </div>
                    </div>
                </div>

                {/* Ações Rápidas */}
                <div className="metric-card glass-panel">
                    <div className="metric-header">
                        <h3>Ações Rápidas</h3>
                    </div>
                    <div className="quick-actions">
                        <button className="btn btn-outline w-full mb-3">
                            <RefreshCw size={16} /> Atualizar Telemetria
                        </button>
                        <button className="btn btn-danger-outline w-full">
                            <StopCircle size={16} /> PARADA GLOBAL (KILL SWITCH)
                        </button>
                    </div>
                </div>
            </div>

            <div className="logs-section glass-panel">
                <h3 className="section-title">Auditoria em Tempo Real</h3>
                <table className="logs-table">
                    <thead>
                        <tr>
                            <th>Hora</th>
                            <th>Origem</th>
                            <th>Ação</th>
                            <th>Destino</th>
                        </tr>
                    </thead>
                    <tbody>
                        {metrics.logs.map((log, i) => (
                            <tr key={i}>
                                <td className="log-time">{log.time}</td>
                                <td>{log.origin}</td>
                                <td><span className="log-action">{log.action}</span></td>
                                <td><span className="log-dest">{log.dest}</span></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <style>{`
        .page-header {
          margin-bottom: 32px;
        }
        .page-title {
          font-size: 2rem;
          color: var(--color-primary);
        }
        .page-subtitle {
          color: var(--color-text-secondary);
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 24px;
          margin-bottom: 32px;
        }

        .metric-card {
          padding: 24px;
        }

        .metric-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 24px;
        }

        .metric-header h3 {
          font-size: 1.125rem;
          margin: 0;
        }

        .text-success { color: var(--color-success); }
        .text-primary { color: var(--color-primary); }
        .text-danger { color: var(--color-danger); }
        .text-warning { color: var(--color-warning); }

        .system-status-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .status-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 12px;
          background: rgba(255, 255, 255, 0.02);
          border-radius: 6px;
          font-size: 0.875rem;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #52525b; /* offline / unknown */
        }
        .status-dot.online {
          background: var(--color-success);
          box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
        }
        
        .stats-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        .stat-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .stat-value {
          font-size: 1.25rem;
          font-weight: 700;
        }

        .stat-label {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
        }

        .w-full { width: 100%; }
        .mb-3 { margin-bottom: 12px; }

        .logs-section {
          padding: 24px;
        }

        .section-title {
          font-size: 1.125rem;
          margin-bottom: 24px;
          color: var(--color-text-primary);
        }

        .logs-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }

        .logs-table th {
          text-align: left;
          padding: 12px 16px;
          color: var(--color-text-secondary);
          border-bottom: 1px solid var(--color-border);
          font-weight: 500;
        }

        .logs-table td {
          padding: 16px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .log-time {
          color: var(--color-primary);
          font-family: monospace;
        }

        .log-action {
          background: rgba(255, 255, 255, 0.05);
          padding: 4px 8px;
          border-radius: 4px;
          font-family: monospace;
        }

        .log-dest {
          color: var(--color-text-secondary);
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;
          justify-content: center;
          transition: all 0.2s;
        }

        .btn-outline {
          background: transparent;
          color: var(--color-primary);
          border: 1px solid var(--color-primary);
        }
        .btn-outline:hover { background: rgba(212, 175, 55, 0.1); }
        
        .btn-danger-outline {
          background: transparent;
          color: var(--color-danger);
          border: 1px solid var(--color-danger);
        }
        .btn-danger-outline:hover { background: rgba(239, 68, 68, 0.1); }
      `}</style>
        </div >
    );
}
