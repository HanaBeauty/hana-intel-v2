from src.celery_app import celery_app
from src.database import async_session_maker
from sqlalchemy.future import select
from sqlalchemy import or_
from src.models import Campaign, CampaignStatus
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

async def run_hunter_logic():
    """Lógica assíncrona real do caçador de oportunidades"""
    logger.info("Iniciando Caçador de Oportunidades Hana Intel (Shopify + CrewAI)...")
    
    from src.shopify_hunter_api import shopify_hunter_api
    from src.agents_crew import crew_content_lab
    
    async with async_session_maker() as db:
        # 1. Buscar Oportunidades (Checkouts Abandonados)
        checkouts = await shopify_hunter_api.fetch_abandoned_checkouts(limit=5)
        
        # 2. Buscar Oportunidades (Clientes VIP Inativos)
        inativos = await shopify_hunter_api.fetch_inactive_vip_customers(limit=5)
        
        todas_oportunidades = checkouts + inativos
        
        if not todas_oportunidades:
            logger.info("Caçador de Oportunidades: Nenhuma oportunidade urgente encontrada.")
            return

        novas_campanhas = []
        for op in todas_oportunidades:
            try:
                # Vamos delegar o roteiro (copywriting) para o CrewAI Content Lab
                if op["type"] == "abandoned_cart":
                    # WhatsApp Recovery
                    contexto = (
                        f"O cliente '{op['customer_name']}' abandonou o carrinho de compras. "
                        f"O valor total do carrinho é R$ {op['total_price']}. "
                        f"Os itens no carrinho são: {', '.join(op['items'])}.\n"
                        f"Crie uma mensagem curta, consultiva e humanizada de WHATSAPP (com emojis apropriados) para que a atendente recupere a venda. "
                        f"Não dê descontos agressivos de imediato, mas se ofereça para ajudar com dúvidas técnicas sobre o produto."
                    )
                    
                    logger.info(f"Enviando para CrewAI (Carrinho): {op['customer_name']} / {op.get('email')}")
                    # Enviar para a thread pool do agent sincrono (run in thread para não travar celery loop)
                    copy_gerada = await asyncio.to_thread(crew_content_lab.process_campaign, contexto, "mensagem de WhatsApp")
                    
                    campanha = Campaign(
                        title=f"Carrinho Abandonado - {op['customer_name']}",
                        intent="Recuperação de Carrinho",
                        channel="whatsapp",
                        target_audience=f"{op['customer_name']} ({op.get('phone') or op.get('email')})",
                        generated_content=copy_gerada,
                        status=CampaignStatus.draft
                    )
                    novas_campanhas.append(campanha)
                    
                elif op["type"] == "inactive_vip":
                    # Email VIP
                    contexto = (
                        f"O cliente VIP '{op['customer_name']}' está inativo há {op['days_inactive']} dias. "
                        f"Ele já gastou R$ {op['total_spent']} na nossa loja no passado.\n"
                        f"Crie o CONTEÚDO de um E-MAIL Premium focando em relacionamento, novidades e oferecendo um voucher secreto 'VIP15' de 15% OFF em toda a compra.\n"
                        f"Retorne o resultado final EMBUTIDO EXATAMENTE dentro das TAGS HTML seguras do layout padronizado da Hana. "
                        f"Retorne apenas o HTML completo entre as tags <html>...</html>."
                    )
                    
                    # Vamos inserir o template HTML como string base para o agente utilizar
                    html_template = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
body { font-family: 'Inter', Arial, sans-serif; background-color: #FAFAFA; margin: 0; padding: 0; color: #222222; }
.container { max-width: 600px; margin: 0 auto; background-color: #FFFFFF; overflow: hidden; border: 1px solid #EAEAEA; }
.header { padding: 35px 20px; text-align: center; } .logo { width: 170px; margin-bottom: 25px; }
.hero { background: #111111; padding: 55px 25px; text-align: center; color: #FFFFFF; }
.hero h1 { font-size: 26px; }
.content-box { padding: 45px 35px; line-height: 1.8; font-size: 15px; color: #444444; }
.btn-product { background: #111111; color: #FFFFFF; padding: 16px 35px; text-decoration: none; display: inline-block; font-size: 12px; }
</style></head>
<body><div class="container">
<div class="header"><h1>HANA BEAUTY</h1></div>
<div class="hero"><h1>[TITULO AQUI]</h1></div>
<div class="content-box">[SEU TEXTO AQUI]<br><br><a href="#" class="btn-product">Acessar Oferta VIP</a></div>
</div></body></html>"""

                    contexto += f"\n\nTEMPLATE OBRIGATÓRIO (NÃO ALTERE O CSS, APENAS PREENCHA OS MOLDES):\n{html_template}"
                    
                    logger.info(f"Enviando para CrewAI (Inativo VIP): {op['customer_name']} / {op.get('email')}")
                    copy_gerada = await asyncio.to_thread(crew_content_lab.process_campaign, contexto, "código HTML de e-mail")
                    
                    campanha = Campaign(
                        title=f"Retenção VIP - {op['customer_name']}",
                        intent="Retenção Inativos VIP",
                        channel="email",
                        target_audience=f"{op['customer_name']} ({op.get('email')})",
                        generated_content=copy_gerada,
                        status=CampaignStatus.draft
                    )
                    novas_campanhas.append(campanha)
                    
            except Exception as e:
                logger.error(f"Erro ao processar oportunidade para {op.get('customer_name')}: {e}")
                
        if novas_campanhas:
            db.add_all(novas_campanhas)
            await db.commit()
            logger.info(f"✅ Caçador de Oportunidades: {len(novas_campanhas)} Rascunhos gerados por IA enviados ao Review Board.")

@celery_app.task(name="tasks.opportunity_hunter")
def opportunity_hunter_task():
    """
    Worker autônomo. Roda em background pelo Celery Beat todo dia de manhã.
    Analisa compras paradas, abandono de carrinho, aniversários.
    Gera rascunhos de campanhas na tabela Campaign com status 'draft'.
    """
    logger.info("Celery [opportunity_hunter_task] disparada.")
    # Executa a coroutine no event loop sincrono do celery block
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_hunter_logic())
    return {"status": "success", "message": "Oportunidades caçadas concluídas."}
