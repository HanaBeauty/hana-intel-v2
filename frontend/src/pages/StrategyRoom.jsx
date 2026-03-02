import { useState } from 'react';
import { Activity, Beaker, ShieldAlert, Cpu } from 'lucide-react';

export default function StrategyRoom() {
  const [socialActive, setSocialActive] = useState(false);
  return (
    <div className="strategy-room animate-fade-in">
      <header className="page-header">
        <div>
          <h1 className="page-title">Strategy Room</h1>
          <p className="page-subtitle">Centro Neurológico de Orquestração da Inteligência Artificial</p>
        </div>
      </header>

      <div className="layout-grid">
        {/* Orquestração de Agentes */}
        <div className="agents-panel glass-panel">
          <div className="panel-header">
            <Cpu className="text-primary" size={24} />
            <h3>Orquestração CrewAI</h3>
          </div>

          <div className="agent-cards">
            {/* Agente de Atendimento */}
            <div className="agent-card">
              <div className="agent-header">
                <div>
                  <h4>Hana Master (Atendimento)</h4>
                  <span className="agent-status online">Online & Roteando</span>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
              <p className="agent-desc">Responsável por triar e rotear o atendimento primário via WhatsApp.</p>
            </div>

            {/* Agente Tira Dúvidas */}
            <div className="agent-card">
              <div className="agent-header">
                <div>
                  <h4>Hana Expert (Técnica)</h4>
                  <span className="agent-status online">Online na Base RAG</span>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
              <p className="agent-desc">Dotado com o Manual Técnico Hana. Lê a documentação sobre adesivos, retenção e Lash Designers.</p>
            </div>

            {/* Agente Social */}
            <div className="agent-card">
              <div className="agent-header">
                <div>
                  <h4>Hana Social (Community)</h4>
                  <span className={`agent-status ${socialActive ? 'online' : 'standby'}`}>
                    {socialActive ? 'Online & Postando' : 'Standby'}
                  </span>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" checked={socialActive} onChange={() => setSocialActive(!socialActive)} />
                  <span className="slider"></span>
                </label>
              </div>
              <p className="agent-desc">Postagens de conteúdo para grupos e status diário.</p>
            </div>
          </div>
        </div>

        <div className="right-col">
          {/* Master Prompt */}
          <div className="master-prompt-panel glass-panel">
            <div className="panel-header">
              <Beaker className="text-warning" size={24} />
              <h3>The Master Prompt (Diretriz Global)</h3>
            </div>
            <textarea
              className="prompt-textarea"
              defaultValue="Você é a Hana. Você respira o DNA Black/Gold da Hana Beauty. Seu objetivo primário é atuar com frieza técnica e um altíssimo padrão para Lash Designers experientes, vendendo a segurança dos nossos adesivos."
            />
            <div className="actions">
              <button className="btn btn-outline">Atualizar Frequência Cerebral</button>
            </div>
          </div>

          {/* Regras de Ouro */}
          <div className="rules-panel glass-panel">
            <div className="panel-header">
              <ShieldAlert className="text-danger" size={24} />
              <h3>Regras Inflexíveis (Guardrails)</h3>
            </div>
            <ul className="guardrails-list">
              <li>Nunca confirmar troca/devolução de Adesivo se estiver aberto há mais de 30 dias.</li>
              <li>Sempre encaminhar para o humano no WhatsApp ao detectar irritação ocular.</li>
              <li>Não oferecer descontos que superem 15% sem autorização via Review Board.</li>
            </ul>
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

        .layout-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
        }
        
        .right-col {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .panel-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 24px;
        }

        .panel-header h3 {
          font-size: 1.125rem;
          margin: 0;
          color: var(--color-text-primary);
        }

        .text-primary { color: var(--color-primary); }
        .text-warning { color: var(--color-warning); }
        .text-danger { color: var(--color-danger); }

        .agents-panel, .master-prompt-panel, .rules-panel {
          padding: 24px;
        }

        .agent-cards {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .agent-card {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.05);
          padding: 20px;
          border-radius: 8px;
        }

        .agent-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 12px;
        }

        .agent-header h4 {
          margin: 0 0 4px 0;
          font-size: 1rem;
          color: var(--color-text-primary);
        }

        .agent-status {
          font-size: 0.75rem;
          padding: 2px 8px;
          border-radius: 4px;
        }

        .agent-status.online {
          background: rgba(16, 185, 129, 0.1);
          color: var(--color-success);
        }
        
        .agent-status.standby {
          background: rgba(255, 255, 255, 0.05);
          color: var(--color-text-secondary);
        }

        .agent-desc {
          margin: 0;
          font-size: 0.85rem;
          color: var(--color-text-secondary);
          line-height: 1.5;
        }

        .prompt-textarea {
          width: 100%;
          height: 150px;
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid var(--color-border);
          border-radius: 8px;
          padding: 16px;
          color: var(--color-text-primary);
          font-family: 'Courier New', Courier, monospace;
          resize: vertical;
          outline: none;
          transition: border-color 0.2s;
        }

        .prompt-textarea:focus {
          border-color: var(--color-primary);
        }

        .actions {
          margin-top: 16px;
          display: flex;
          justify-content: flex-end;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s;
        }

        .btn-outline {
          background: transparent;
          color: var(--color-primary);
          border: 1px solid var(--color-primary);
        }

        .btn-outline:hover {
          background: rgba(212, 175, 55, 0.1);
        }

        .guardrails-list {
          padding-left: 20px;
          margin: 0;
          color: var(--color-text-secondary);
          line-height: 1.6;
          font-size: 0.9rem;
        }
        
        .guardrails-list li {
          margin-bottom: 8px;
        }

        /* Toggle Switch CSS */
        .toggle-switch {
          position: relative;
          display: inline-block;
          width: 44px;
          height: 24px;
        }

        .toggle-switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }

        .slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #333;
          transition: .4s;
          border-radius: 24px;
        }

        .slider:before {
          position: absolute;
          content: "";
          height: 18px;
          width: 18px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: .4s;
          border-radius: 50%;
        }

        input:checked + .slider {
          background-color: var(--color-primary);
        }

        input:focus + .slider {
          box-shadow: 0 0 1px var(--color-primary);
        }

        input:checked + .slider:before {
          transform: translateX(20px);
        }
      `}</style>
    </div>
  );
}
