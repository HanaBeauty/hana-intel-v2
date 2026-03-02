import { useState } from 'react';
import { Sparkles, CalendarDays, BookOpen, Send, Zap, Save } from 'lucide-react';

export default function NurtureHub() {
  const [cards, setCards] = useState([
    {
      id: 1,
      tag: 'Técnica: Umidade',
      tagClass: 'tag-technical',
      time: 'Gerado há 2 horas',
      title: 'O Segredo Oculto do Ar Condicionado no Efeito Falsa Colagem',
      body: '"Bom dia, comunidade Ouro! ✨ Notou que seus fios estão soltando mais rápido essa semana? Antes de culpar o adesivo, olhe para a saída de ar do seu estúdio. O vento direto acelera a cura e pode causar uma falsa colagem..."',
      isEditing: false
    },
    {
      id: 2,
      tag: 'Posicionamento Premium',
      tagClass: 'tag-mindset',
      time: 'Gerado ontem às 18:00',
      title: 'Não brigue por preço, justifique com retenção.',
      body: 'O mercado está cheio de quem cobra barato. Você não é mais uma na multidão. Assuma seu valor cobrando pela segurança do seu procedimento...',
      isEditing: false,
      isEmail: true
    }
  ]);

  const handleToggleEdit = (id) => {
    setCards(cards.map(c => c.id === id ? { ...c, isEditing: !c.isEditing } : c));
  };

  const handleSave = (id, newBody) => {
    setCards(cards.map(c => c.id === id ? { ...c, body: newBody, isEditing: false } : c));
    // Em produção aqui dispararia um fetch PUT
  };

  return (
    <div className="nurture-hub animate-fade-in">
      <header className="page-header">
        <div>
          <h1 className="page-title">Nurture Hub</h1>
          <p className="page-subtitle">Motor Autônomo de Nutrição e Autoridade da Comunidade</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={() => alert('Disparando Celery Nurture Task...')}>
            <Zap size={18} /> Forçar Insight Agora
          </button>
        </div>
      </header>

      <div className="layout-grid">
        {/* Painel Esquerdo: Fila de Conteúdo e Dicas */}
        <div className="content-col">
          <div className="panel-header">
            <Sparkles className="text-warning" size={24} />
            <h2>Dicas & Pílulas Prontas (Aprovação)</h2>
          </div>

          <div className="content-deck">
            {cards.map(card => (
              <div key={card.id} className="content-card">
                <div className="card-header">
                  <span className={`badge ${card.tagClass}`}>{card.tag}</span>
                  <span className="timestamp">{card.time}</span>
                </div>
                <h3 className="content-title">{card.title}</h3>

                {card.isEditing ? (
                  <textarea
                    className="edit-nurture-textarea"
                    defaultValue={card.body}
                    id={`edit-${card.id}`}
                  />
                ) : (
                  card.isEmail ? (
                    <div className="email-preview-box">
                      <h4>[E-mail HTML - Tema Preto/Dourado]</h4>
                      <p>{card.body}</p>
                    </div>
                  ) : (
                    <p className="content-body">{card.body}</p>
                  )
                )}

                <div className="card-actions">
                  {card.isEditing ? (
                    <button className="btn btn-primary-sm" onClick={() => handleSave(card.id, document.getElementById(`edit-${card.id}`).value)}>
                      <Save size={14} /> Salvar Alterações
                    </button>
                  ) : (
                    <button className="btn btn-outline-sm" onClick={() => handleToggleEdit(card.id)}>
                      <BookOpen size={14} /> Editar Copy
                    </button>
                  )}
                  <button className="btn btn-primary-sm">
                    <Send size={14} /> {card.isEmail ? 'Aprovar disparo de E-mail' : 'Aprovar p/ Grupos WhatsApp'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Coluna Direita: Controle Editorial */}
        <div className="sidebar-col">
          <div className="glass-panel schedule-panel">
            <div className="panel-header">
              <CalendarDays className="text-primary" size={24} />
              <h3>Calendário Editorial AI</h3>
            </div>

            <div className="timeline">
              <div className="timeline-item">
                <div className="marker done"></div>
                <div className="content">
                  <strong>Terça-feira</strong>
                  <span>Técnica (Dica de Retenção)</span>
                  <small>Status: Disparado 🟢</small>
                </div>
              </div>
              <div className="timeline-item">
                <div className="marker active"></div>
                <div className="content">
                  <strong>Quinta-feira</strong>
                  <span>Motivacional (Story de Engajamento)</span>
                  <small>Status: Pendente Revisão 🟡</small>
                </div>
              </div>
              <div className="timeline-item">
                <div className="marker pending"></div>
                <div className="content">
                  <strong>Sábado</strong>
                  <span>E-mail Marketing (Novidade / Catálogo)</span>
                  <small>Status: Aguardando Criação ⚪</small>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel config-panel mt-4">
            <h3>Configurações do Hub</h3>
            <p className="text-muted mb-3 mt-1 text-sm">Regras de negócio que o AI Lab respeita ao criar.</p>

            <div className="form-group mb-3">
              <label className="text-sm">Frequência Autônoma</label>
              <select className="form-select w-100 bg-dark text-white border-secondary p-2 rounded mt-1">
                <option>1 Dica a cada 2 dias (Recomendado)</option>
                <option>1 Dica diária</option>
                <option>Apenas sob demanda (Manual)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="text-sm">Tom de Voz</label>
              <select className="form-select w-100 bg-dark text-white border-secondary p-2 rounded mt-1">
                <option>Premium Ouro (Educativo Rígido)</option>
                <option>Amigável/Inspiracional (Comunidade)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
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
          grid-template-columns: 2fr 1fr;
          gap: 24px;
        }

        .panel-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 24px;
        }
        
        .panel-header h2, .panel-header h3 {
          margin: 0;
          color: var(--color-text-primary);
        }

        .text-primary { color: var(--color-primary); }
        .text-warning { color: var(--color-warning); }

        .content-deck {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .content-card {
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid rgba(212, 175, 55, 0.15); /* Gold tint border */
          border-radius: 8px;
          padding: 24px;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .content-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0,0,0,0.5);
          border-color: rgba(212, 175, 55, 0.4);
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .badge {
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
        }

        .tag-technical { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3);}
        .tag-mindset { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3);}

        .timestamp {
          font-size: 0.8rem;
          color: var(--color-text-secondary);
        }

        .content-title {
          font-size: 1.25rem;
          margin-top: 0;
          margin-bottom: 12px;
          color: var(--color-text-primary);
        }

        .content-body {
          font-family: Georgia, serif;
          font-style: italic;
          color: #cccccc;
          line-height: 1.6;
          margin-bottom: 20px;
          padding-left: 16px;
          border-left: 3px solid var(--color-primary);
        }

        .email-preview-box {
          background: #0a0a0b;
          border: 1px solid #333;
          padding: 16px;
          border-radius: 6px;
          margin-bottom: 20px;
        }

        .email-preview-box h4 {
          margin: 0 0 8px 0;
          color: var(--color-primary);
          font-size: 0.85rem;
          text-transform: uppercase;
        }

        .email-preview-box p {
          margin: 0;
          color: #aaa;
          font-size: 0.9rem;
        }

        .card-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          border-top: 1px dashed rgba(255,255,255,0.1);
          padding-top: 16px;
        }

        .btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-weight: 600;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: var(--color-primary);
          color: #000;
          padding: 10px 20px;
          border: none;
        }

        .btn-primary:hover {
          background: var(--color-primary-light);
        }

        .btn-primary-sm {
          background: var(--color-primary);
          color: #000;
          padding: 8px 16px;
          border: none;
          font-size: 0.85rem;
        }

        .btn-outline-sm {
          background: transparent;
          color: var(--color-text-primary);
          border: 1px solid var(--color-border);
          padding: 8px 16px;
          font-size: 0.85rem;
        }

        .btn-outline-sm:hover {
          border-color: var(--color-primary);
          color: var(--color-primary);
        }

        /* Sidebar Col */
        .glass-panel {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          padding: 24px;
        }

        .mt-4 { margin-top: 24px; }
        .mb-3 { margin-bottom: 16px; }
        .text-sm { font-size: 0.875rem; }
        .text-muted { color: var(--color-text-secondary); }

        .edit-nurture-textarea {
          width: 100%;
          min-height: 120px;
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid var(--color-primary);
          border-radius: 4px;
          color: #fff;
          padding: 12px;
          font-family: inherit;
          font-size: 0.9rem;
          margin-bottom: 16px;
          resize: vertical;
          outline: none;
        }

        /* Timeline */
        .timeline {
          display: flex;
          flex-direction: column;
          gap: 20px;
          position: relative;
          padding-left: 20px;
        }

        .timeline::before {
          content: '';
          position: absolute;
          left: 6px;
          top: 0;
          bottom: 0;
          width: 2px;
          background: rgba(255,255,255,0.1);
        }

        .timeline-item {
          position: relative;
        }

        .marker {
          position: absolute;
          left: -20px;
          top: 4px;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          transform: translateX(-50%);
          border: 3px solid #000;
        }

        .marker.done { background: var(--color-success); }
        .marker.active { background: var(--color-warning); box-shadow: 0 0 8px rgba(245, 158, 11, 0.6); }
        .marker.pending { background: #555; }

        .content strong {
          display: block;
          color: var(--color-text-primary);
          margin-bottom: 4px;
        }

        .content span {
          display: block;
          color: #ccc;
          font-size: 0.9rem;
          margin-bottom: 4px;
        }

        .content small {
          color: var(--color-text-secondary);
        }
      `}</style>
    </div>
  );
}
