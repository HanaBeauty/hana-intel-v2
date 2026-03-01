import { useState } from 'react';
import { Mail, MessageCircle, Check, X, FileEdit } from 'lucide-react';

export default function ReviewBoard() {
    const [drafts, setDrafts] = useState([
        {
            id: 1,
            title: 'Adesivo Sokkyoku - Frio e Umidade',
            channel: 'email',
            audience: 'Clientes Inativos Sul/Sudeste',
            content: 'Aproveite o frio para garantir a retenção perfeita com nosso Adesivo Sokkyoku...',
            status: 'Aguardando Aprovação'
        },
        {
            id: 2,
            title: 'Recuperação Carrinho Abandonado',
            channel: 'whatsapp',
            audience: 'Maria Fernanda',
            content: 'Oie, vi que você deixou o Gel Base na sacola! Quer uma ajudinha?',
            status: 'Aguardando Aprovação'
        }
    ]);

    return (
        <div className="review-page animate-fade-in">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Review Board</h1>
                    <p className="page-subtitle">Aprovador de Campanhas e CRM Inteligente</p>
                </div>
            </header>

            <div className="strategy-input-container glass-panel">
                <h3 className="section-title">Sala de Estratégia (IA)</h3>
                <textarea
                    placeholder="Ex: Hana, escreva um e-mail para as clientes do Adesivo Butil oferecendo 10% de desconto na reposição esta semana..."
                    className="strategy-textarea"
                ></textarea>
                <div className="strategy-actions">
                    <button className="btn btn-outline">
                        <FileEdit size={16} /> Rascunhar Campanha
                    </button>
                </div>
            </div>

            <h3 className="section-title mt-8">Aguardando sua Aprovação</h3>

            <div className="cards-list">
                {drafts.map(draft => (
                    <div key={draft.id} className="draft-card glass-panel">
                        <div className="draft-header">
                            <div className={`channel-badge ${draft.channel}`}>
                                {draft.channel === 'email' ? <Mail size={16} /> : <MessageCircle size={16} />}
                                {draft.channel.toUpperCase()}
                            </div>
                            <h4>{draft.title}</h4>
                        </div>

                        <div className="draft-meta">
                            <span><strong>Alvo:</strong> {draft.audience}</span>
                            <span className="status-warning">{draft.status}</span>
                        </div>

                        <div className="draft-content">
                            {draft.content}
                        </div>

                        <div className="draft-actions">
                            <button className="btn btn-danger-outline">
                                <X size={16} /> Descartar
                            </button>
                            <button className="btn btn-success">
                                <Check size={16} /> Aprovar e Disparar
                            </button>
                        </div>
                    </div>
                ))}
                {drafts.length === 0 && (
                    <div className="empty-state">
                        <p>Nenhuma campanha aguardando revisão.</p>
                    </div>
                )}
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

        .section-title {
          font-size: 1.125rem;
          color: var(--color-text-primary);
          margin-bottom: 16px;
        }
        
        .mt-8 { margin-top: 32px; }

        .strategy-input-container {
          padding: 24px;
          margin-bottom: 32px;
        }

        .strategy-textarea {
          width: 100%;
          min-height: 100px;
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid var(--color-border);
          border-radius: 8px;
          padding: 16px;
          color: var(--color-text-primary);
          font-family: inherit;
          resize: vertical;
          outline: none;
          transition: border-color 0.2s;
        }

        .strategy-textarea:focus {
          border-color: var(--color-primary);
        }

        .strategy-actions {
          margin-top: 16px;
          display: flex;
          justify-content: flex-end;
        }

        .cards-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .draft-card {
          padding: 24px;
        }

        .draft-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .channel-badge {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 10px;
          border-radius: 6px;
          font-size: 0.75rem;
          font-weight: 600;
        }

        .channel-badge.email {
          background: rgba(59, 130, 246, 0.15);
          color: #60a5fa;
        }

        .channel-badge.whatsapp {
          background: rgba(16, 185, 129, 0.15);
          color: #34d399;
        }

        .draft-header h4 {
          font-size: 1.125rem;
          margin: 0;
        }

        .draft-meta {
          display: flex;
          justify-content: space-between;
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          margin-bottom: 16px;
          padding-bottom: 16px;
          border-bottom: 1px solid var(--color-border);
        }

        .status-warning {
          color: var(--color-warning);
          background: rgba(245, 158, 11, 0.1);
          padding: 2px 8px;
          border-radius: 4px;
        }

        .draft-content {
          background: #000;
          padding: 16px;
          border-radius: 8px;
          font-family: 'Courier New', Courier, monospace;
          color: #d1d5db;
          margin-bottom: 24px;
          white-space: pre-wrap;
        }

        .draft-actions {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
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

        .btn-success {
          background: var(--color-success);
          color: #fff;
        }

        .btn-success:hover {
          background: #059669;
        }

        .btn-danger-outline {
          background: transparent;
          color: var(--color-danger);
          border: 1px solid var(--color-danger);
        }

        .btn-danger-outline:hover {
          background: rgba(239, 68, 68, 0.1);
        }

        .empty-state {
          padding: 40px;
          text-align: center;
          color: var(--color-text-secondary);
          background: rgba(255, 255, 255, 0.02);
          border-radius: 12px;
          border: 1px dashed var(--color-border);
        }
      `}</style>
        </div>
    );
}
