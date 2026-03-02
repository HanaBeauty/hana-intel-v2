import { useState } from 'react';
import { Mail, MessageCircle, Check, X, FileEdit } from 'lucide-react';

export default function ReviewBoard() {
  const [drafts, setDrafts] = useState([
    {
      id: 1,
      title: 'Adesivo Sokkyoku - Frio e Umidade',
      channel: 'email',
      audience: 'Clientes Inativos Sul/Sudeste',
      content: `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Outfit:wght@300;400;600&display=swap');
                body { font-family: 'Inter', Arial, sans-serif; background-color: #FAFAFA; margin: 0; padding: 0; color: #222222; }
                .container { max-width: 600px; margin: 0 auto; background-color: #FFFFFF; overflow: hidden; border: 1px solid #EAEAEA; }
                
                /* Header */
                .header { padding: 35px 20px; text-align: center; background: #FFFFFF; }
                .logo { width: 170px; margin-bottom: 25px; }
                .nav { border-top: 1px solid #EAEAEA; border-bottom: 1px solid #EAEAEA; padding: 15px 0; text-align: center; }
                .nav a { text-decoration: none; color: #555555; font-size: 11px; font-weight: 600; margin: 0 12px; text-transform: uppercase; letter-spacing: 1.5px; transition: color 0.3s; }
                .nav a.highlight { color: #BFA15F; } /* Premium Gold */
                
                /* Hero */
                .hero { background: #111111; padding: 55px 25px; text-align: center; color: #FFFFFF; }
                .hero-tag { border: 1px solid #BFA15F; color: #BFA15F; display: inline-block; padding: 6px 20px; font-size: 10px; margin-bottom: 25px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; }
                .hero h1 { margin: 0; font-family: 'Outfit', sans-serif; font-size: 26px; font-weight: 400; text-transform: uppercase; letter-spacing: 1.5px; line-height: 1.4; }
                
                /* Content */
                .content-box { padding: 45px 35px; line-height: 1.8; font-size: 15px; color: #444444; font-weight: 300; text-align: justify; }
                .content-box b { font-weight: 600; color: #111111; }
                
                /* Highlights */
                .highlights { background: #FAFAFA; padding: 30px; margin: 35px 0; border-left: 2px solid #BFA15F; }
                .highlights ul { list-style: none; padding: 0; margin: 0; }
                .highlights li { margin-bottom: 15px; font-weight: 400; font-size: 14px; display: flex; align-items: flex-start; }
                .highlights li::before { content: '■'; color: #BFA15F; font-size: 10px; margin-right: 12px; margin-top: 5px; }
                .highlights li:last-child { margin-bottom: 0; }
                
                /* Product Box */
                .product-box { border: 1px solid #EAEAEA; padding: 40px 30px; text-align: center; background: #FFFFFF; margin-top: 35px; }
                .product-name { font-family: 'Outfit', sans-serif; font-size: 20px; color: #111111; display: block; margin-bottom: 25px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;}
                .btn-product { background: #111111; color: #FFFFFF !important; padding: 16px 35px; text-decoration: none; font-weight: 600; display: inline-block; font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; transition: background 0.3s; border: 1px solid #111111; }
                
                /* WhatsApp Channel Promo */
                .wa-promo { background: #111111; padding: 35px; text-align: center; margin-top: 45px; border-radius: 2px; }
                .wa-promo h3 { margin: 0 0 15px 0; font-family: 'Outfit', sans-serif; font-size: 18px; color: #FFFFFF; font-weight: 400; letter-spacing: 1px; text-transform: uppercase; }
                .wa-promo p { font-size: 14px; color: #CCCCCC; margin-bottom: 25px; line-height: 1.6; font-weight: 300; }
                .btn-wa { background: #25D366; color: #FFFFFF !important; padding: 14px 28px; text-decoration: none; font-weight: 600; display: inline-block; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; border-radius: 2px; }
                
                /* Footer */
                .footer { background: #FAFAFA; border-top: 1px solid #EAEAEA; padding: 50px 30px; text-align: center; color: #777777; font-size: 12px; line-height: 1.6; font-weight: 300; }
                .social-icons { margin-bottom: 35px; text-align: center; }
                .social-icons a { display: inline-block; text-decoration: none; margin: 0 8px; }
                .social-icons img { width: 18px; filter: grayscale(100%) opacity(0.6); transition: all 0.3s; }
                .footer-text { margin-bottom: 25px; color: #666666; }
                .footer-text b { color: #111111; font-weight: 600; font-size: 13px; letter-spacing: 1px; text-transform: uppercase;}
                .unsubscribe { color: #111111; text-decoration: underline; margin-top: 25px; display: block; font-size: 11px; font-weight: 600; }
                .footer-disclaimer { font-size: 10px; color: #999999; max-width: 480px; margin: 0 auto; line-height: 1.5; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://www.hanabeauty.com.br/cdn/shop/files/Logotipo-Hanabeauty1.png?v=1690976695&width=300" alt="Hana Beauty" class="logo">
                    <div class="nav">
                        <a href="https://www.hanabeauty.com.br/collections/cilios">Cílios</a>
                        <a href="https://www.hanabeauty.com.br/collections/unhas">Unhas</a>
                        <a href="https://www.hanabeauty.com.br/collections/pinceis">Pincéis</a>
                        <a href="https://www.hanabeauty.com.br/collections/ofertas" class="highlight">Ofertas VIP</a>
                    </div>
                </div>

                <div class="hero">
                    <div class="hero-tag">Tecnologia Japonesa</div>
                    <h1>Zero Etil + Zero Carbono = Segurança Máxima</h1>
                </div>

                <div class="content-box">
                    Olá, Lash Designer! Como fornecedor premium para profissionais como você, sabemos que atender clientes com sensibilidade química é um desafio técnico real. Apresentamos o Adesivo Butil AmLash - a única cola do mercado com dupla exclusão: ZERO ETIL-CIANOACRILATO e ZERO CARBONO.<br><br>Desenvolvido com tecnologia japonesa e base de Butil-Cianoacrilato (componente utilizado em suturas cirúrgicas hospitalares), este adesivo oferece polimerização suave (3-4s) e é a solução técnica definitiva para clientes com histórico de sensibilidade aos adesivos convencionais.<br><br>Benefícios imediatos para seu negócio:<br>- Amplie seu público-alvo incluindo clientes sensíveis<br>- Reduza riscos de reações alérgicas com formulação quimicamente limpa<br>- Mantenha a qualidade Hana Beauty com pigmento Purple Dye para visualização<br>- Ofereça conforto superior com baixa emissão de vapores<br><br>Transforme um nicho desafiador em sua especialidade e fortaleça sua autoridade no mercado.<img src="https://www.adsai.com.br/t/o/{{msg_id}}" width="1" height="1" style="display:none !important;" />

                    <div class="highlights">
                        <ul style="margin:0; padding:0;"><li>Base Cirúrgica Butil</li><li>Sem Etil e Carbono</li><li>Segurança Comprovada</li></ul>
                    </div>

                    <div class="product-box">
                        
                        <span class="product-name">Adesivo Butil AmLash – Para Pele Sensível | Reduz Irritação | Não Hipoalergênico - Tecnologia Japonesa</span>
                        <a href="https://www.hanabeauty.com.br/products/adesivo-butil-amlash-para-extensao-de-cilios-2ml?utm_source=hana_beauty_crm&utm_medium=email&utm_campaign=hana_intel_automation" class="btn-product">Garanta Sua Vantagem Técnica</a>
                    </div>

                    <div class="wa-promo">
                        <h3>Acesso Restrito e Informação Direta</h3>
                        <p>Assine nosso Canal Oficial no WhatsApp. Um ambiente dedicado ao envio periódico de boletins técnicos, atualizações sobre tecnologias globais de beleza e condições comerciais reservadas exclusivamente para a nossa comunidade.</p>
                        <a href="https://whatsapp.com/channel/0029VawDM0BFnSz9hFrEF41B" class="btn-wa">Ingressar no Canal Oficial</a>
                    </div>
                </div>

                <div class="footer">
                    <div class="social-icons">
                        <a href="https://www.instagram.com/hanabeautyoficial/" title="Instagram"><img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png" alt="Instagram"></a>
                        <a href="https://www.facebook.com/HanaBeautyAtendimento" title="Facebook"><img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" alt="Facebook"></a>
                        <a href="https://www.youtube.com/@hanabeauty1907" title="YouTube"><img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" alt="YouTube"></a>
                        <a href="https://www.tiktok.com/@hanabeautyoficial" title="TikTok"><img src="https://cdn-icons-png.flaticon.com/512/3046/3046121.png" alt="TikTok"></a>
                        <a href="https://linkedin.com/company/hana-beauty-imp-exp-ltda" title="LinkedIn"><img src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png" alt="LinkedIn"></a>
                        <a href="https://www.pinterest.com/hanabeautyoficial" title="Pinterest"><img src="https://cdn-icons-png.flaticon.com/512/3536/3536559.png" alt="Pinterest"></a>
                        <a href="https://twitter.com/_HanaBeauty" title="X"><img src="https://cdn-icons-png.flaticon.com/512/5969/5969020.png" alt="X"></a>
                        <a href="https://wa.me/5511947393315" title="WhatsApp"><img src="https://cdn-icons-png.flaticon.com/512/733/733585.png" alt="WhatsApp"></a>
                    </div>

                    <div class="footer-text">
                        <b>Hana Beauty</b><br>
                        Avenida Getúlio Vargas, 1089, 08560-000 Poá SP, Brasil<br>
                        WhatsApp (11) 94739-3315 • <a href="mailto:faleconosco@hanabeauty.com.br" style="color:#666666; text-decoration: none;">faleconosco@hanabeauty.com.br</a>
                    </div>

                    <div class="footer-disclaimer">
                        O compromisso com a sua segurança e a privacidade de seus dados é diretriz basilar em nossas operações. A Hana Beauty reitera que jamais solicitará informações pessoais por e-mail. Em caso de recebimento de comunicações com este teor, pedimos que desconsidere imediatamente.
                    </div>

                    <a href="https://www.adsai.com.br/u/{{unsub_token}}" class="unsubscribe">Gerenciar preferências ou cancelar assinatura</a>
                    <div style="margin-top: 25px; opacity: 0.6; font-size: 10px;">© 2026 Hana Beauty. Todos os direitos reservados.</div>
                </div>
            </div>
        </body>
        </html>
      `,
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

            <div className={`draft-content ${draft.channel === 'email' ? 'email-preview' : ''}`}>
              {draft.channel === 'email' ? (
                <div dangerouslySetInnerHTML={{ __html: draft.content }} />
              ) : (
                draft.content
              )}
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

        .email-preview {
          background: transparent;
          padding: 0;
          border-radius: 0;
          font-family: inherit;
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
