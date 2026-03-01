import { useState, useEffect } from 'react';
import { ShieldAlert, Bot, User, CheckCircle2 } from 'lucide-react';

export default function Radar() {
    // Estado simulado até plugarmos na API
    const [activeChats, setActiveChats] = useState([
        { id: '5511999999999', name: 'Maria Fernanda', status: 'bot_active', lastMsg: 'Qual adesivo para alergia?' },
        { id: '5511988888888', name: 'Juliana Lash', status: 'handoff', lastMsg: 'Vou querer dois kits.' },
    ]);

    return (
        <div className="radar-page animate-fade-in">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Radar 360</h1>
                    <p className="page-subtitle">Monitoramento em Tempo Real do Atendimento Inteligente</p>
                </div>
                <div className="status-badge pulse">
                    <span className="dot online"></span>
                    IA Operacional
                </div>
            </header>

            <div className="chats-grid">
                {activeChats.map(chat => (
                    <div key={chat.id} className="chat-card glass-panel">
                        <div className="chat-header">
                            <div className="chat-avatar">
                                <User size={20} />
                            </div>
                            <div className="chat-info">
                                <h3>{chat.name}</h3>
                                <span className="phone-number">{chat.id}</span>
                            </div>
                            <div className={`mode-badge ${chat.status === 'bot_active' ? 'active' : 'paused'}`}>
                                {chat.status === 'bot_active' ? <Bot size={16} /> : <ShieldAlert size={16} />}
                                {chat.status === 'bot_active' ? 'Hana IA' : 'Paralisado (Hand-off)'}
                            </div>
                        </div>

                        <div className="chat-body">
                            <p className="last-message">"{chat.lastMsg}"</p>
                        </div>

                        <div className="chat-actions">
                            {chat.status === 'handoff' ? (
                                <button className="btn btn-primary" onClick={() => console.log('Reativar IA')}>
                                    <Bot size={16} /> Reativar Piloto Automático (/bot_on)
                                </button>
                            ) : (
                                <button className="btn btn-danger" onClick={() => console.log('Silenciar IA')}>
                                    <ShieldAlert size={16} /> Assumir Atendimento (/bot_off)
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <style>{`
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 40px;
        }

        .page-title {
          font-size: 2rem;
          color: var(--color-primary);
        }

        .page-subtitle {
          color: var(--color-text-secondary);
          margin-top: 4px;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          background: rgba(16, 185, 129, 0.1);
          color: var(--color-success);
          padding: 8px 16px;
          border-radius: 20px;
          font-size: 0.875rem;
          border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--color-success);
        }

        .chats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 24px;
        }

        .chat-card {
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .chat-header {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .chat-avatar {
          width: 40px;
          height: 40px;
          background: #27272a;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-text-secondary);
        }

        .chat-info h3 {
          font-size: 1rem;
          margin: 0;
        }

        .phone-number {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
        }

        .mode-badge {
          margin-left: auto;
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.75rem;
          padding: 4px 10px;
          border-radius: 12px;
        }

        .mode-badge.active {
          background: rgba(212, 175, 55, 0.15);
          color: var(--color-primary);
        }

        .mode-badge.paused {
          background: rgba(239, 68, 68, 0.15);
          color: var(--color-danger);
        }

        .chat-body {
          background: rgba(0, 0, 0, 0.3);
          padding: 16px;
          border-radius: 8px;
          border-left: 2px solid var(--color-border);
        }

        .last-message {
          font-style: italic;
          color: var(--color-text-secondary);
        }

        .chat-actions {
          margin-top: auto;
        }

        .btn {
          width: 100%;
          padding: 10px 16px;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: all 0.2s;
        }

        .btn-primary {
          background: var(--color-primary);
          color: #000;
        }

        .btn-primary:hover {
          background: var(--color-primary-hover);
        }

        .btn-danger {
          background: rgba(239, 68, 68, 0.1);
          color: var(--color-danger);
          border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .btn-danger:hover {
          background: rgba(239, 68, 68, 0.2);
        }
      `}</style>
        </div>
    );
}
