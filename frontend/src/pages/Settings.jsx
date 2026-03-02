import { Key, ShieldCheck, Database, Save } from 'lucide-react';

export default function Settings() {
    return (
        <div className="settings-page animate-fade-in">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Configurações Globais</h1>
                    <p className="page-subtitle">Gerenciamento de Integrações, Chaves e Políticas da Inteligência</p>
                </div>
            </header>

            <div className="settings-grid">
                {/* Integrações API */}
                <div className="settings-panel glass-panel">
                    <div className="panel-header">
                        <Key className="text-primary" size={24} />
                        <h3>Chaves de API & Conexões</h3>
                    </div>

                    <div className="form-group">
                        <label>OpenAI (GPT-4) API Key</label>
                        <input type="password" placeholder="sk-..." defaultValue="sk-proj-xxxxxxxxxxxxxxxxxxxx" className="form-input" />
                        <small>Usada para o motor de raciocínio avançado do Master Agent.</small>
                    </div>

                    <div className="form-group">
                        <label>Evolution API (WhatsApp) - Endpoint</label>
                        <input type="text" defaultValue="https://evo1.infordes.io" className="form-input" />
                    </div>

                    <div className="form-group">
                        <label>Evolution API (WhatsApp) - Global API Key</label>
                        <input type="password" placeholder="Key..." defaultValue="xxxx-evo-api-key" className="form-input" />
                    </div>

                    <div className="form-group">
                        <label>Shopify Access Token (Admin API)</label>
                        <input type="password" placeholder="shpat_..." defaultValue="shpat_xxxxxxxxxxxxxxxxxxxx" className="form-input" />
                        <small>Usada para Rastreio de Pedidos e leitura de Carrinhos Abandonados.</small>
                    </div>

                    <button className="btn btn-primary mt-4">
                        <Save size={16} /> Salvar Chaves
                    </button>
                </div>

                <div className="right-col">
                    {/* Segurança Anti-Spam */}
                    <div className="settings-panel glass-panel">
                        <div className="panel-header">
                            <ShieldCheck className="text-success" size={24} />
                            <h3>Anti-Fadiga & Segurança (CRM)</h3>
                        </div>

                        <div className="form-group">
                            <label>Bloqueio Anti-Spam (Horas)</label>
                            <div className="range-slider-container">
                                <input type="range" min="1" max="168" defaultValue="48" className="range-slider" />
                                <span className="range-value">48 horas</span>
                            </div>
                            <small>Tempo mínimo de isolamento do cliente antes da IA sugerir um novo E-mail ou WhatsApp corporativo para ele. (Evita banimento de conta na Evolution).</small>
                        </div>

                        <div className="form-group mt-4">
                            <label>Handoff Timer (Horas)</label>
                            <div className="range-slider-container">
                                <input type="range" min="1" max="48" defaultValue="12" className="range-slider" />
                                <span className="range-value">12 horas</span>
                            </div>
                            <small>Tempo que a IA fica calada ("bot_off") após 1 intervenção de Humano no atendimento ao vivo.</small>
                        </div>

                        <button className="btn btn-outline mt-4">
                            <Save size={16} /> Atualizar Políticas
                        </button>
                    </div>

                    {/* RAG */}
                    <div className="settings-panel glass-panel">
                        <div className="panel-header">
                            <Database className="text-info" size={24} />
                            <h3>Base de Conhecimento RAG (Vector DB)</h3>
                        </div>

                        <div className="rag-status">
                            <div className="stat-row">
                                <span>Motor Vetorial:</span>
                                <strong>PostgreSQL + pgvector</strong>
                            </div>
                            <div className="stat-row">
                                <span>Último Crawler (Shopify):</span>
                                <strong>Hoje, às 08:30 BRT</strong>
                            </div>
                            <div className="stat-row">
                                <span>Documentos em Memória L2:</span>
                                <strong>1,204 chunks</strong>
                            </div>
                        </div>

                        <div className="actions mt-4">
                            <button className="btn btn-outline">Forçar Sincronização Shopify Agora</button>
                        </div>
                    </div>
                </div>
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

        .settings-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
        }
        
        .right-col {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .settings-panel {
          padding: 24px;
        }

        .panel-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 24px;
          border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
          padding-bottom: 16px;
        }

        .panel-header h3 {
          font-size: 1.125rem;
          margin: 0;
          color: var(--color-text-primary);
        }

        .text-primary { color: var(--color-primary); }
        .text-success { color: var(--color-success); }
        .text-info { color: #3b82f6; }

        .form-group {
          margin-bottom: 20px;
        }

        .form-group label {
          display: block;
          font-size: 0.9rem;
          font-weight: 500;
          color: var(--color-text-primary);
          margin-bottom: 8px;
        }
        
        .form-group small {
          display: block;
          color: var(--color-text-secondary);
          margin-top: 6px;
          font-size: 0.8rem;
          line-height: 1.4;
        }

        .form-input {
          width: 100%;
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid var(--color-border);
          border-radius: 6px;
          padding: 12px 16px;
          color: var(--color-text-primary);
          font-family: inherit;
          outline: none;
          transition: border-color 0.2s;
        }

        .form-input:focus {
          border-color: var(--color-primary);
        }

        /* Range Slider */
        .range-slider-container {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        
        .range-slider {
          flex: 1;
          -webkit-appearance: none;
          background: rgba(0, 0, 0, 0.4);
          height: 6px;
          border-radius: 4px;
          outline: none;
        }
        
        .range-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: var(--color-primary);
          cursor: pointer;
        }
        
        .range-value {
          font-weight: 600;
          color: var(--color-primary);
          min-width: 70px;
          text-align: right;
        }

        /* RAG Status */
        .rag-status {
          background: rgba(0, 0, 0, 0.2);
          padding: 16px;
          border-radius: 8px;
          border: 1px solid rgba(255,255,255,0.05);
        }
        
        .stat-row {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .stat-row:last-child {
          border-bottom: none;
        }
        
        .stat-row span {
          color: var(--color-text-secondary);
        }
        
        .stat-row strong {
          color: var(--color-text-primary);
        }

        .mt-4 { margin-top: 24px; }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: all 0.2s;
          cursor: pointer;
        }

        .btn-primary {
          background: var(--color-primary);
          color: #000;
        }

        .btn-primary:hover {
          background: var(--color-primary-light);
        }
        
        .btn-outline {
          background: transparent;
          color: var(--color-text-primary);
          border: 1px solid var(--color-border);
        }

        .btn-outline:hover {
          border-color: var(--color-primary);
          color: var(--color-primary);
        }
      `}</style>
        </div>
    );
}
