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

      {/* --- Novo: Hub de Mensageria (Absorvido da V1) --- */}
      <div className="hub-section glass-panel">
        <h3 className="section-title">Hub de Mensageria Autônoma</h3>
        <div className="hub-stats-grid">
          <div className="hub-stat-card">
            <span className="hub-label">Total Enviados</span>
            <span className="hub-value text-primary">2.597</span>
            <div className="hub-subtext">Hoje</div>
          </div>
          <div className="hub-stat-card">
            <span className="hub-label">Saúde da IA (Entrega)</span>
            <span className="hub-value text-success">98.5%</span>
          </div>
          <div className="hub-stat-card">
            <span className="hub-label">Taxa Média (Open/CTR)</span>
            <span className="hub-value text-warning">14% / 3.2%</span>
          </div>
          <div className="hub-stat-card">
            <span className="hub-label">Fluxos Autônomos Ativos</span>
            <span className="hub-value">4</span>
            <div className="hub-subtext">Celery Workers</div>
          </div>
        </div>

        <h4 className="subsection-title">Automações em Execução</h4>
        <div className="automation-cards">
          <div className="auto-card">
            <div className="auto-header">
              <span className="auto-tag success">ACTIVE</span>
              <span className="auto-channel">WHATSAPP</span>
            </div>
            <h5>FLOW | ABANDONO_CARRINHO</h5>
            <p>Recuperação de checkout abandonado (Gatilho: 30min)</p>
          </div>

          <div className="auto-card">
            <div className="auto-header">
              <span className="auto-tag success">ACTIVE</span>
              <span className="auto-channel">EMAIL</span>
            </div>
            <h5>SEQ | POST_PURCHASE_VIP</h5>
            <p>Nutrição LTV Ouro após compra efetuada.</p>
          </div>

          <div className="auto-card">
            <div className="auto-header">
              <span className="auto-tag warning">PAUSED</span>
              <span className="auto-channel">WHATSAPP</span>
            </div>
            <h5>FLOW | BOAS_VINDAS</h5>
            <p>Pausado temporariamente pelo Anti-Spam Shield</p>
          </div>
        </div>
      </div>

      <div className="logs-section glass-panel mt-6">
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
        
        /* Hub de Mensageria */
        .hub-section {
          padding: 24px;
          margin-bottom: 32px;
        }

        .hub-stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 32px;
        }

        .hub-stat-card {
          background: rgba(0, 0, 0, 0.2);
          border: 1px solid rgba(255, 255, 255, 0.05);
          padding: 16px;
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .hub-label {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .hub-value {
          font-size: 1.5rem;
          font-weight: 700;
        }

        .hub-subtext {
          font-size: 0.75rem;
          color: #666;
        }

        .subsection-title {
          font-size: 1rem;
          color: var(--color-text-primary);
          margin-bottom: 16px;
          font-weight: 500;
        }

        .automation-cards {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 16px;
        }

        .auto-card {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.05);
          padding: 20px;
          border-radius: 8px;
          transition: transform 0.2s, background 0.2s;
        }

        .auto-card:hover {
          background: rgba(255, 255, 255, 0.02);
          transform: translateY(-2px);
        }

        .auto-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .auto-tag {
          font-size: 0.65rem;
          font-weight: 700;
          padding: 2px 6px;
          border-radius: 4px;
        }

        .auto-tag.success { background: rgba(16, 185, 129, 0.1); color: var(--color-success); }
        .auto-tag.warning { background: rgba(245, 158, 11, 0.1); color: var(--color-warning); }
        
        .auto-channel {
          font-size: 0.7rem;
          color: var(--color-text-secondary);
          letter-spacing: 1px;
        }

        .auto-card h5 {
          font-size: 1rem;
          color: var(--color-text-primary);
          margin: 0 0 8px 0;
        }

        .auto-card p {
          font-size: 0.8rem;
          color: var(--color-text-secondary);
          margin: 0;
          line-height: 1.4;
        }
        
        .mt-6 { margin-top: 24px; }

      `}</style>
    </div >
  );
}
