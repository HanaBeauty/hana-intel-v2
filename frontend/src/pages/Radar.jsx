import { useState, useEffect, useRef } from 'react';
import { Search, Send, ShieldAlert, Bot, User, CheckCircle2, ChevronRight, Archive, ArrowRightLeft, MessageSquare, Users, MessageCircle } from 'lucide-react';

export default function Radar() {
  const [activeChats, setActiveChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [leadProfile, setLeadProfile] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);

  // Novos States para o CRM
  const [activeTab, setActiveTab] = useState('live'); // 'live' ou 'contacts'
  const [contactList, setContactList] = useState([]);
  const [totalContacts, setTotalContacts] = useState(0);
  const [pageSize, setPageSize] = useState(50);
  const [currentPage, setCurrentPage] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchChats = async () => {
    try {
      const res = await fetch('/api/v1/dashboard/chat/active');
      if (res.ok) {
        const data = await res.json();
        setActiveChats(data);
      }
    } catch (err) {
      console.error('Erro ao buscar conversas:', err);
    }
  };

  const fetchHistory = async (chatId) => {
    try {
      const res = await fetch(`/api/v1/dashboard/chat/${chatId}/history`);
      if (res.ok) {
        const data = await res.json();
        setChatHistory(data);
      }
    } catch (err) {
      console.error('Erro ao buscar histórico:', err);
    }
  };

  const fetchProfile = async (chatId) => {
    try {
      setLeadProfile(null); // Reset during loading
      const res = await fetch(`/api/v1/dashboard/crm/lead/${chatId}`);
      if (res.ok) {
        const data = await res.json();
        setLeadProfile(data);
      }
    } catch (err) {
      console.error('Erro ao buscar perfil CRM:', err);
    }
  };

  const fetchContacts = async () => {
    try {
      const offset = currentPage * pageSize;
      let url = `/api/v1/dashboard/contacts/list?limit=${pageSize}&offset=${offset}`;
      if (searchQuery) {
        url += `&q=${encodeURIComponent(searchQuery)}`;
      }
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setContactList(data.contacts || []);
        setTotalContacts(data.total_count || 0);
      }
    } catch (err) {
      console.error('Erro ao buscar lista de contatos:', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'live') {
      fetchChats();
      const interval = setInterval(fetchChats, 5000); // Polling 5s
      return () => clearInterval(interval);
    } else if (activeTab === 'contacts') {
      fetchContacts();
    }
  }, [activeTab, pageSize, currentPage, searchQuery]);

  // Reset page when searching
  useEffect(() => {
    setCurrentPage(0);
  }, [searchQuery]);

  useEffect(() => {
    if (selectedChat) {
      fetchHistory(selectedChat.id);
      fetchProfile(selectedChat.id);
      const interval = setInterval(() => fetchHistory(selectedChat.id), 3000); // Polling 3s
      return () => clearInterval(interval);
    } else {
      setChatHistory([]);
      setLeadProfile(null);
    }
  }, [selectedChat]);

  // Scroll to bottom when history changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedChat) return;

    const msgToSend = newMessage;
    setNewMessage('');

    // Add optimistic message to UI
    setChatHistory(prev => [...prev, { sender: 'admin', text: msgToSend, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);

    try {
      await fetch(`/api/v1/dashboard/chat/${selectedChat.id}/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: msgToSend })
      });
      // A atualização do modo vai ocorrer na próxima varredura do polling (handoff vira pausado)
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
    }
  };

  return (
    <div className="radar-layout">
      {/* HEADER LOCAL (CHAVEADOR) */}
      <div className="radar-toggle-header">
        <div className="radar-title-area">
          <h1>Radar 360º</h1>
          <span className="subtitle">Visualização Mestre da Torre de Controle</span>
        </div>

        <div className="radar-tabs">
          <button
            className={`radar-tab ${activeTab === 'live' ? 'active' : ''}`}
            onClick={() => setActiveTab('live')}
          >
            <MessageCircle size={18} /> Live Chat
          </button>
          <button
            className={`radar-tab ${activeTab === 'contacts' ? 'active' : ''}`}
            onClick={() => setActiveTab('contacts')}
          >
            <Users size={18} /> Base de Contatos
          </button>
        </div>
      </div>

      <div className="radar-master-detail animate-fade-in">

        {activeTab === 'live' ? (
          <>
            {/* COLUNA 1: Lista de Conversas */}
            <div className="radar-col-list">
              <div className="col-header">
                <h2>Conversas Ativas</h2>
                <div className="search-bar">
                  <Search size={16} />
                  <input type="text" placeholder="Buscar cliente..." />
                </div>
              </div>

              <div className="chat-list">
                {activeChats.map(chat => (
                  <div
                    key={chat.id}
                    className={`chat-list-item ${selectedChat?.id === chat.id ? 'selected' : ''}`}
                    onClick={() => setSelectedChat(chat)}
                  >
                    <div className="avatar"><User size={20} /></div>
                    <div className="chat-summary">
                      <div className="chat-top">
                        <span className="chat-name">{chat.name}</span>
                        <span className="chat-time">AGORA</span>
                      </div>
                      <div className="chat-bottom">
                        <span className="chat-preview">{chat.lastMsg}</span>
                        {chat.status === 'bot_active' ? (
                          <Bot size={14} className="status-icon active" />
                        ) : (
                          <ShieldAlert size={14} className="status-icon paused" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* COLUNA 2: O Palco (Histórico do Chat) */}
            <div className="radar-col-chat glass-panel">
              {selectedChat ? (
                <>
                  <div className="chat-header-main">
                    <div className="chat-person-info">
                      <h3>Conversa com {selectedChat.name} ({selectedChat.id})</h3>
                      <span className={`status-pill ${selectedChat.status}`}>
                        {selectedChat.status === 'bot_active' ? 'Ativo via Hana IA' : 'Pausado (Hand-off Humano)'}
                      </span>
                    </div>
                  </div>

                  <div className="chat-history">
                    {chatHistory.map((msg, i) => (
                      <div key={i} className={`message-bubble-wrapper ${msg.sender}`}>
                        <div className={`message-bubble ${msg.sender}`}>
                          <span className="message-sender-name">
                            {msg.sender === 'user' ? selectedChat.name : msg.sender === 'admin' ? 'Juliano Takimoto (Humano)' : 'Hana Intel (IA)'} • {msg.time}
                          </span>
                          <p>{msg.text}</p>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>

                  <div className="chat-input-area">
                    <form onSubmit={handleSendMessage} className="chat-form">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Interceptar e digitar mensagem como atendente humano..."
                        className="chat-input"
                        title="Ao enviar, o modo Hand-off será ativado automaticamente."
                      />
                      <button type="submit" className="btn-send">
                        <Send size={18} />
                      </button>
                    </form>
                  </div>
                </>
              ) : (
                <div className="empty-chat-state">
                  <MessageSquare size={48} className="empty-icon" />
                  <h3>Selecione uma conversa</h3>
                  <p>Monitore a IA ou assuma o atendimento em tempo real.</p>
                </div>
              )}
            </div>
          </>
        ) : (
          /* COLUNA UNIFICADA: CRM DATAGRID */
          <div className="radar-col-datagrid glass-panel">
            <div className="datagrid-header">
              <h2>Gestão de Leads & Clientes ({contactList.length})</h2>
              <div className="search-bar">
                <Search size={16} />
                <input
                  type="text"
                  placeholder="Buscar por nome, e-mail ou telefone..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            <div className="datagrid-table-wrapper">
              <table className="crm-table">
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Telefone (ZAP)</th>
                    <th>Ticket / LTV</th>
                    <th>E-mail Principal</th>
                    <th>Última Ação</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {contactList.map(contact => (
                    <tr
                      key={contact.id}
                      className={`crm-row ${selectedChat?.id === contact.phone ? 'selected' : ''}`}
                      onClick={() => setSelectedChat({ id: contact.phone, name: contact.name, status: contact.status === 'client' ? 'bot_active' : 'handoff', lastMsg: 'Visualização CRM' })}
                    >
                      <td>
                        <div className="crm-name-cell">
                          <div className="avatar micro"><User size={14} /></div>
                          <strong>{contact.name || 'Desconhecido'}</strong>
                        </div>
                      </td>
                      <td><span className="font-mono">{contact.phone || 'Sem Zap'}</span></td>
                      <td><span className="ltv-value-green">R$ {contact.total_spent}</span></td>
                      <td><span className="email-cell">{contact.email || '--'}</span></td>
                      <td>{new Date(contact.last_interaction).toLocaleDateString('pt-BR')}</td>
                      <td>
                        <span className={`status-pill ${contact.status === 'client' ? 'client' : 'lead'}`}>
                          {contact.status === 'client' ? 'Cliente Vip' : 'Lead Frio'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* CONTROLES DE PAGINAÇÃO */}
            <div className="datagrid-footer">
              <div className="pagination-info">
                Exibindo {contactList.length} de {totalContacts} contatos
              </div>

              <div className="pagination-controls">
                <div className="page-size-selector">
                  <span>Itens por página:</span>
                  {[50, 100, 500].map(size => (
                    <button
                      key={size}
                      className={`btn-size ${pageSize === size ? 'active' : ''}`}
                      onClick={() => { setPageSize(size); setCurrentPage(0); }}
                    >
                      {size}
                    </button>
                  ))}
                </div>

                <div className="page-nav">
                  <button
                    className="btn-nav"
                    disabled={currentPage === 0}
                    onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                  >
                    Anterior
                  </button>
                  <span className="current-page">Página {currentPage + 1}</span>
                  <button
                    className="btn-nav"
                    disabled={(currentPage + 1) * pageSize >= totalContacts}
                    onClick={() => setCurrentPage(prev => prev + 1)}
                  >
                    Próximo
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* COLUNA 3: Perfil do Cliente & Ações */}
        {selectedChat && (
          <div className="radar-col-profile">
            <div className="profile-card glass-panel">
              <div className="profile-header">
                <div className="profile-avatar-large"><User size={32} /></div>
                <h2>{selectedChat.name}</h2>
                {leadProfile ? (
                  <span className={`badge-tier ${leadProfile.badge_class}`}>Nível {leadProfile.tier}</span>
                ) : (
                  <span className="badge-tier silver">Carregando CRM...</span>
                )}
              </div>

              <div className="profile-section">
                <h4>Ações Rápidas</h4>
                <div className="action-grid">
                  <button className="btn-action"><Archive size={16} /> Resolver</button>
                  <button className="btn-action"><ArrowRightLeft size={16} /> Transferir</button>

                  {selectedChat.status === 'handoff' ? (
                    <button className="btn-action highlight"><Bot size={16} /> Reativar IA</button>
                  ) : (
                    <button className="btn-action warning"><ShieldAlert size={16} /> Parar IA</button>
                  )}

                </div>
              </div>

              <div className="profile-section">
                <h4>Performance CRM</h4>
                <div className="crm-stats">
                  <div className="stat-box">
                    <span className="stat-label">LTV Total</span>
                    <span className="stat-value">{leadProfile ? leadProfile.total_spent_formatted : 'R$ --'}</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-label">Pedidos</span>
                    <span className="stat-value">{leadProfile ? leadProfile.orders_count : '-'}</span>
                  </div>
                </div>
              </div>

              <div className="profile-section">
                <h4>Canal Principal</h4>
                <p className="contact-info">+{selectedChat.id}</p>
              </div>
            </div>
          </div>
        )}

        <style>{`
        .radar-layout {
          display: flex;
          flex-direction: column;
          height: calc(100vh - 80px); /* Ajuste basado no header global */
          margin: -20px;
        }

        .radar-toggle-header {
          display: flex; justify-content: space-between; align-items: center;
          padding: 15px 24px;
          background: rgba(0,0,0,0.4);
          border-bottom: 1px solid var(--color-border);
        }

        .radar-title-area h1 { margin: 0; font-size: 1.3rem; color: var(--color-primary); font-weight: 300; }
        .radar-title-area .subtitle { font-size: 0.8rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 1px; }

        .radar-tabs {
          display: flex; gap: 8px;
          background: rgba(255,255,255,0.05); padding: 4px; border-radius: 8px; border: 1px solid var(--color-border);
        }

        .radar-tab {
          display: flex; align-items: center; gap: 8px;
          background: transparent; color: var(--color-text-secondary); border: none;
          padding: 8px 16px; border-radius: 6px; font-weight: 500; font-size: 0.9rem;
          cursor: pointer; transition: 0.3s;
        }
        .radar-tab:hover { color: white; background: rgba(255,255,255,0.05); }
        .radar-tab.active { background: rgba(212, 175, 55, 0.15); color: var(--color-primary); border: 1px solid rgba(212, 175, 55, 0.3); }

        .radar-master-detail {
          display: flex;
          flex: 1;
          min-height: 0;
          gap: 20px;
          padding: 20px;
        }

        /* Coluna 1: Lista */
        .radar-col-list {
          width: 320px;
          border-right: 1px solid var(--color-border);
          display: flex;
          flex-direction: column;
          background: rgba(0,0,0,0.2);
          border-radius: 12px;
          overflow: hidden;
        }

        .col-header {
          padding: 20px;
          border-bottom: 1px solid var(--color-border);
        }
        .col-header h2 { font-size: 1.2rem; margin-bottom: 15px; }

        .search-bar {
          display: flex;
          align-items: center;
          gap: 10px;
          background: rgba(255,255,255,0.05);
          padding: 8px 12px;
          border-radius: 8px;
          border: 1px solid var(--color-border);
        }
        .search-bar input {
          background: transparent; border: none; color: white; outline: none; width: 100%;
        }

        .chat-list {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }

        .chat-list-item {
          display: flex;
          gap: 12px;
          padding: 16px 20px;
          border-bottom: 1px solid rgba(255,255,255,0.02);
          cursor: pointer;
          transition: background 0.2s;
        }
        .chat-list-item:hover { background: rgba(255,255,255,0.05); }
        .chat-list-item.selected { background: rgba(212, 175, 55, 0.1); border-left: 3px solid var(--color-primary); }

        .chat-summary { flex: 1; min-width: 0; }
        .chat-top { display: flex; justify-content: space-between; margin-bottom: 4px; }
        .chat-name { font-weight: 600; font-size: 0.9rem; }
        .chat-time { font-size: 0.7rem; color: var(--color-text-secondary); }
        
        .chat-bottom { display: flex; justify-content: space-between; align-items: center; }
        .chat-preview { 
          font-size: 0.8rem; color: var(--color-text-secondary);
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .status-icon.active { color: var(--color-primary); }
        .status-icon.paused { color: var(--color-danger); }

        /* Coluna 2: Chat */
        .radar-col-chat {
          flex: 1;
          display: flex;
          flex-direction: column;
          border-radius: 12px;
          overflow: hidden;
        }

        .chat-header-main {
          padding: 20px;
          border-bottom: 1px solid var(--color-border);
          background: rgba(0,0,0,0.4);
        }
        .chat-person-info h3 { margin: 0 0 8px 0; font-size: 1.1rem; }
        
        .status-pill {
          display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;
        }
        .status-pill.bot_active { background: rgba(16, 185, 129, 0.1); color: var(--color-success); border: 1px solid rgba(16, 185, 129, 0.3); }
        .status-pill.handoff { background: rgba(239, 68, 68, 0.1); color: var(--color-danger); border: 1px solid rgba(239, 68, 68, 0.3); }

        .chat-history {
          flex: 1;
          padding: 20px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .message-bubble-wrapper { display: flex; width: 100%; }
        .message-bubble-wrapper.user { justify-content: flex-start; }
        .message-bubble-wrapper.bot { justify-content: flex-end; }
        .message-bubble-wrapper.admin { justify-content: flex-end; }

        .message-bubble {
          max-width: 70%;
          padding: 12px 16px;
          border-radius: 12px;
          position: relative;
        }
        
        .message-bubble.user {
          background: rgba(255,255,255,0.05);
          border: 1px solid var(--color-border);
          border-bottom-left-radius: 2px;
        }
        .message-bubble.bot {
          background: rgba(212, 175, 55, 0.15); /* Dourado da Hana */
          border: 1px solid rgba(212, 175, 55, 0.3);
          border-bottom-right-radius: 2px;
        }
        .message-bubble.admin {
          background: rgba(59, 130, 246, 0.15); /* Azul para admin humano */
          border: 1px solid rgba(59, 130, 246, 0.3);
          border-bottom-right-radius: 2px;
        }

        .message-sender-name {
          display: block; font-size: 0.7rem; color: var(--color-text-secondary); margin-bottom: 6px;
        }
        .message-bubble p { margin: 0; font-size: 0.95rem; line-height: 1.4; }

        .chat-input-area {
          padding: 20px;
          border-top: 1px solid var(--color-border);
          background: rgba(0,0,0,0.4);
        }

        .chat-form {
          display: flex; gap: 10px;
        }
        .chat-input {
          flex: 1;
          background: rgba(255,255,255,0.05);
          border: 1px solid var(--color-border);
          padding: 12px 16px;
          border-radius: 8px;
          color: white;
          outline: none;
        }
        .chat-input:focus { border-color: var(--color-primary); }
        
        .btn-send {
          background: var(--color-primary);
          color: black;
          border: none;
          width: 48px;
          border-radius: 8px;
          display: flex; align-items: center; justify-content: center;
          cursor: pointer; transition: 0.2s;
        }
        .btn-send:hover { background: var(--color-primary-hover); transform: scale(1.05); }

        .empty-chat-state {
          flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
          color: var(--color-text-secondary);
        }
        .empty-icon { opacity: 0.3; margin-bottom: 20px; }

        /* Coluna 3: Profile */
        .radar-col-profile {
          width: 320px;
        }
        
        .profile-card {
          padding: 24px;
          display: flex; flex-direction: column; gap: 24px;
        }
        
        .profile-header {
          display: flex; flex-direction: column; align-items: center; gap: 10px; text-align: center;
          padding-bottom: 20px; border-bottom: 1px solid var(--color-border);
        }
        .profile-avatar-large {
          width: 80px; height: 80px; background: rgba(255,255,255,0.1); border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
        }
        .profile-header h2 { margin: 0; font-size: 1.2rem; }
        .badge-tier { font-size: 0.75rem; padding: 4px 12px; border-radius: 12px; font-weight: 600; transition: 0.3s; }
        .badge-tier.bronze { background: rgba(205, 127, 50, 0.2); color: #eab308; border: 1px solid rgba(205, 127, 50, 0.4); } /* Adjust gold-ish bronze for dark mode */
        .badge-tier.silver { background: rgba(160, 174, 192, 0.2); color: #cbd5e1; border: 1px solid rgba(160,174,192,0.4); }
        .badge-tier.gold { background: rgba(212, 175, 55, 0.2); color: #facc15; border: 1px solid rgba(212, 175, 55, 0.4); }
        .badge-tier.gray { background: rgba(100, 100, 100, 0.2); color: #9ca3af; border: 1px solid rgba(100, 100, 100, 0.4); }
        .badge-tier.red { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }

        .profile-section h4 { font-size: 0.8rem; text-transform: uppercase; color: var(--color-text-secondary); margin-bottom: 12px; }
        
        .action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        
        .btn-action {
          background: rgba(255,255,255,0.05); border: 1px solid var(--color-border); color: var(--color-text-primary);
          padding: 10px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; gap: 6px;
          font-size: 0.75rem; cursor: pointer; transition: 0.2s;
        }
        .btn-action:hover { background: rgba(255,255,255,0.1); }
        .btn-action.highlight { border-color: var(--color-primary); color: var(--color-primary); }
        .btn-action.highlight:hover { background: rgba(212, 175, 55, 0.1); }
        .btn-action.warning { border-color: var(--color-danger); color: var(--color-danger); }
        .btn-action.warning:hover { background: rgba(239, 68, 68, 0.1); }

        .crm-stats { display: flex; gap: 12px; }
        .stat-box { flex: 1; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; border: 1px solid var(--color-border); }
        .stat-box .stat-label { display: block; font-size: 0.7rem; color: var(--color-text-secondary); margin-bottom: 4px; }
        .stat-box .stat-value { font-size: 1.1rem; font-weight: 600; color: var(--color-primary); }

        .contact-info { font-size: 0.9rem; font-family: monospace; }

        /* Datagrid CRM View */
        .radar-col-datagrid {
          flex: 1;
          display: flex;
          flex-direction: column;
          border-radius: 12px;
          overflow: hidden;
          background: rgba(0,0,0,0.4);
        }

        .datagrid-header {
          display: flex; justify-content: space-between; align-items: center;
          padding: 20px; border-bottom: 1px solid var(--color-border);
        }
        .datagrid-header h2 { margin: 0; font-size: 1.2rem; font-weight: 400; color: white; }

        .datagrid-table-wrapper {
          flex: 1; overflow: auto; padding: 0;
        }

        .crm-table {
          width: 100%; border-collapse: collapse; text-align: left;
        }
        .crm-table th {
          position: sticky; top: 0; background: rgba(10,10,10,0.95); z-index: 10;
          padding: 16px 20px; font-size: 0.75rem; text-transform: uppercase; color: var(--color-text-secondary);
          border-bottom: 1px solid var(--color-border);
        }
        .crm-table td {
          padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.02);
          font-size: 0.9rem; color: #e2e8f0;
        }
        
        .crm-row { cursor: pointer; transition: 0.2s; }
        .crm-row:hover { background: rgba(255,255,255,0.03); }
        .crm-row.selected { background: rgba(212, 175, 55, 0.08); }

        .crm-name-cell { display: flex; align-items: center; gap: 10px; }
        .avatar.micro { width: 24px; height: 24px; background: rgba(255,255,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--color-primary); }

        .font-mono { font-family: monospace; font-size: 0.85rem; color: #9ca3af; }
        .ltv-value-green { color: var(--color-success); font-weight: 600; }
        .email-cell { color: #9ca3af; font-size: 0.85rem; }

        .status-pill.client { background: rgba(212, 175, 55, 0.1); color: var(--color-primary); border: 1px solid rgba(212, 175, 55, 0.3); }
        .status-pill.lead { background: rgba(100, 100, 100, 0.2); color: #9ca3af; border: 1px solid rgba(100, 100, 100, 0.4); }

        .datagrid-footer {
          padding: 16px 24px;
          border-top: 1px solid var(--color-border);
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: rgba(0,0,0,0.2);
        }

        .pagination-info { font-size: 0.85rem; color: var(--color-text-secondary); }
        
        .pagination-controls { display: flex; align-items: center; gap: 24px; }
        
        .page-size-selector { display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: var(--color-text-secondary); }
        
        .btn-size {
          background: rgba(255,255,255,0.05); border: 1px solid var(--color-border);
          color: white; padding: 4px 10px; border-radius: 4px; cursor: pointer; transition: 0.2s;
        }
        .btn-size:hover { background: rgba(255,255,255,0.1); }
        .btn-size.active { background: var(--color-primary); color: black; border-color: var(--color-primary); }
        
        .page-nav { display: flex; align-items: center; gap: 12px; }
        
        .btn-nav {
          background: rgba(255,255,255,0.05); border: 1px solid var(--color-border);
          color: white; padding: 6px 16px; border-radius: 6px; cursor: pointer; transition: 0.2s;
          font-size: 0.85rem;
        }
        .btn-nav:hover:not(:disabled) { background: rgba(255,255,255,0.1); border-color: var(--color-primary); }
        .btn-nav:disabled { opacity: 0.3; cursor: not-allowed; }
        
        .current-page { font-size: 0.9rem; color: var(--color-primary); font-weight: 600; }

      `}</style>
      </div>
    </div>
  );
}
