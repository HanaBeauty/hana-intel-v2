import { useState, useEffect } from 'react';
import { Mail, MessageCircle, Check, X, FileEdit, RefreshCw, Save } from 'lucide-react';

export default function ReviewBoard() {
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVariations, setSelectedVariations] = useState({}); // { campaignId: 'A' | 'B' | 'C' }
  const [editingContent, setEditingContent] = useState({}); // { campaignId: string }

  const fetchDrafts = async () => {
    try {
      const resp = await fetch('/api/v1/dashboard/campaigns/pending');
      const data = await resp.json();
      setDrafts(data);

      // Inicializa variantes selecionadas (padrão 'A')
      const initialVars = {};
      data.forEach(d => {
        initialVars[d.id] = 'A';
      });
      setSelectedVariations(initialVars);
    } catch (err) {
      console.error("Erro ao carregar rascunhos:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrafts();
  }, []);

  const handleApprove = async (id) => {
    if (!confirm("Confirmar disparo desta campanha?")) return;
    try {
      await fetch(`/api/v1/dashboard/campaigns/${id}/approve`, { method: 'POST' });
      setDrafts(drafts.filter(d => d.id !== id));
    } catch (err) {
      alert("Erro ao aprovar: " + err.message);
    }
  };

  const handleRegenerate = async (id) => {
    try {
      await fetch(`/api/v1/dashboard/campaigns/${id}/regenerate`, { method: 'POST' });
      alert("Solicitação enviada! A IA está gerando novas opções.");
    } catch (err) {
      alert("Erro ao regenerar: " + err.message);
    }
  };

  const handleSaveEdit = async (id) => {
    try {
      const content = editingContent[id];
      await fetch(`/api/v1/dashboard/campaigns/${id}/update`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });
      alert("Editado com sucesso!");
      fetchDrafts(); // Recarrega
      setEditingContent({ ...editingContent, [id]: null });
    } catch (err) {
      alert("Erro ao salvar: " + err.message);
    }
  };

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
        {loading ? (
          <div className="empty-state">Carregando rascunhos...</div>
        ) : drafts.map(draft => {
          const variants = draft.variations ? JSON.parse(draft.variations) : null;
          const currentVar = selectedVariations[draft.id] || 'A';
          const displayContent = editingContent[draft.id] !== undefined ? editingContent[draft.id] : (variants ? variants[currentVar] : draft.content);

          return (
            <div key={draft.id} className="draft-card glass-panel">
              <div className="draft-header">
                <div className={`channel-badge ${draft.channel}`}>
                  {draft.channel === 'email' ? <Mail size={16} /> : <MessageCircle size={16} />}
                  {draft.channel.toUpperCase()}
                </div>
                <h4>{draft.title}</h4>
                <div className="draft-actions ml-auto">
                  <button className="btn btn-outline-sm" onClick={() => handleRegenerate(draft.id)} title="Regenerar com IA">
                    <RefreshCw size={16} /> Regenerar
                  </button>
                </div>
              </div>

              <div className="draft-meta">
                <span><strong>Alvo:</strong> {draft.audience || "Base Geral"}</span>
                {variants && (
                  <div className="variant-tabs">
                    {['A', 'B', 'C'].map(v => (
                      <button
                        key={v}
                        className={`v-tab ${currentVar === v ? 'active' : ''}`}
                        onClick={() => setSelectedVariations({ ...selectedVariations, [draft.id]: v })}
                      >
                        Variante {v}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className={`draft-content ${draft.channel === 'email' ? 'email-preview' : ''}`}>
                {editingContent[draft.id] !== undefined ? (
                  <textarea
                    className="edit-textarea"
                    value={displayContent}
                    onChange={(e) => setEditingContent({ ...editingContent, [draft.id]: e.target.value })}
                  />
                ) : (
                  draft.channel === 'email' ? (
                    <iframe
                      title={`email-preview-${draft.id}`}
                      srcDoc={displayContent}
                      className="email-iframe"
                      sandbox="allow-same-origin"
                    />
                  ) : (
                    displayContent
                  )
                )}
              </div>

              <div className="draft-actions">
                {editingContent[draft.id] !== undefined ? (
                  <button className="btn btn-primary" onClick={() => handleSaveEdit(draft.id)}>
                    <Save size={16} /> Salvar Edição
                  </button>
                ) : (
                  <button className="btn btn-outline" onClick={() => setEditingContent({ ...editingContent, [draft.id]: displayContent })}>
                    <FileEdit size={16} /> Editar
                  </button>
                )}

                <button className="btn btn-danger-outline">
                  <X size={16} /> Descartar
                </button>
                <button className="btn btn-success" onClick={() => handleApprove(draft.id)}>
                  <Check size={16} /> Aprovar e Disparar
                </button>
              </div>
            </div>
          );
        })}
        {!loading && drafts.length === 0 && (
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

        .email-iframe {
          width: 100%;
          height: 600px;
          border: none;
          background: #FAFAFA;
          border-radius: 8px;
        }

        .ml-auto { margin-left: auto; }

        .variant-tabs {
          display: flex;
          gap: 8px;
        }

        .v-tab {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--color-border);
          color: var(--color-text-secondary);
          padding: 4px 12px;
          border-radius: 4px;
          font-size: 0.75rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .v-tab:hover {
          border-color: var(--color-primary);
          color: var(--color-primary);
        }

        .v-tab.active {
          background: var(--color-primary);
          color: #000;
          border-color: var(--color-primary);
          font-weight: 600;
        }

        .edit-textarea {
          width: 100%;
          min-height: 400px;
          background: #000;
          color: #d1d5db;
          border: 1px solid var(--color-primary);
          border-radius: 4px;
          padding: 16px;
          font-family: inherit;
          resize: vertical;
          outline: none;
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
