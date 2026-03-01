from src.celery_app import celery_app
from src.database import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy import or_
from src.models import Campaign, CampaignStatus
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

async def run_hunter_logic():
    """Lógica assíncrona real do caçador de oportunidades"""
    logger.info("Iniciando Caçador de Oportunidades Hana Intel...")
    
    async with AsyncSessionLocal() as db:
        # TODO: No futuro, faremos match real com a tabela Customers da Shopify.
        # Por hora, geramos oportunidades mockadas com base em eventos que a IA observaria
        
        # Oportunidade 1: LTV Alto (Vip) Inativos > 30 dias -> Oferta Exclusiva
        # Mockando a criação de 1 campanha de email
        new_campaign_email = Campaign(
            title="Oferta VIP Exclusiva - Você Sumiu!",
            intent="Retenção VIP",
            channel="email",
            target_audience="Clientes VIP inativos 30d (LTV > R$1.000)",
            generated_content='''
            <div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto; background-color: #0F0F11; color: #E0E0E0; border: 1px solid #333; border-radius: 8px; overflow: hidden;">
                <div style="text-align: center; padding: 30px 20px; background-color: #0A0A0B; border-bottom: 2px solid #D4AF37;">
                    <h1 style="color: #D4AF37; margin: 0; font-size: 24px;">HANA BEAUTY VIP</h1>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #FFF; font-size: 20px; margin-top: 0;">Sentimos sua falta, Lash Ouro! ✨</h2>
                    <p style="line-height: 1.6; color: #A0AEC0;">
                    Reparamos que faz um tempo desde seu último reabastecimento. A excelência do seu estúdio não pode parar.
                    </p>
                    <p style="line-height: 1.6; color: #A0AEC0;">
                    Liberamos um voucher de <strong>15% OFF + Frete Grátis</strong> em toda linha de Pinças de Precisão, exclusivo no seu CPF.
                    </p>
                </div>
            </div>
            ''',
            status=CampaignStatus.draft
        )
        
        # Oportunidade 2: Abandono de Carrinho
        new_campaign_wpp = Campaign(
            title="Carrinho Abandonado - Kit Lash Completo",
            intent="Fechamento de Venda",
            channel="whatsapp",
            target_audience="Mariana (+5511999998888)",
            generated_content="Oie Mari, aqui é da Hana! Vi que o Kit Volume Russo ficou no carrinho. Precisava de ajuda com os detalhes da pinça ou posso garantir seus 10% de cashback para finalizar agora?",
            status=CampaignStatus.draft
        )
        
        db.add_all([new_campaign_email, new_campaign_wpp])
        await db.commit()
        
        logger.info("Caçador de Oportunidades: 2 Rascunhos de Campanha gerados para aprovação no Review Board.")

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
