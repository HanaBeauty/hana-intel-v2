import os
import redis
import httpx
import asyncio
import logging
from src.celery_app import celery_app
from src.database import async_session_maker
from sqlalchemy.future import select
from src.models import Campaign, CampaignStatus
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(redis_url, decode_responses=True)

async def process_campaign_dispatch(campaign_id: int):
    """
    Motor centralizado de disparo com Escudo Anti-Fadiga.
    Substitui a lógica da V1, agrupando CRM e disparo.
    """
    logger.info(f"Iniciando tentativa de disparo para Campanha ID: {campaign_id}")
    
    r = get_redis_client()
    
    async with async_session_maker() as db:
        query = select(Campaign).where(Campaign.id == campaign_id)
        result = await db.execute(query)
        campaign = result.scalars().first()
        
        if not campaign:
            logger.error("Campanha não encontrada para disparo.")
            return
            
        if campaign.status != CampaignStatus.approved:
            logger.warning("Campanha não está aprovada. Cancelando disparo.")
            return

        # Escudo Anti-Fadiga: Verifica quando foi o Último Contato Ativo
        # Para fins de simulação/MVP, assumimos que target_audience possui o número extraído (ex: "Mariana (+5511999998888)")
        # Na versão final em produção, leríamos de uma tabela "CampaignDelivery" por cliente.
        
        # Simulação simples de extração de número
        try:
            target_number = campaign.target_audience.split("(+")[1].split(")")[0]
        except IndexError:
            target_number = None

        if target_number:
            fatigue_key = f"anti_spam_shield:{target_number}"
            # O Admin aprovou. Se este cliente recebeu algo nas últimas 48h (está no Redis), bloqueamos.
            if r.exists(fatigue_key):
                ttl = r.ttl(fatigue_key)
                hours_left = round(ttl / 3600, 1)
                logger.warning(f"🛡️ ANTI-FADIGA: Bloqueando envio para {target_number}. Próxima janela em {hours_left}h.")
                # Podemos marcar o status como falha ou "skipped_fatigue" 
                # (Vou usar 'failed_or_bounced' mas adicionar log de fadiga no futuro)
                campaign.status = CampaignStatus.failed_or_bounced
                await db.commit()
                return
        
        # Sem bloqueio: disparar.
        EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
        EVOLUTION_API_TOKEN = os.getenv("EVOLUTION_API_TOKEN")
        
        if not EVOLUTION_API_URL or not EVOLUTION_API_TOKEN:
            logger.error("Credenciais da Evolution não configuradas.")
            return

        try:
            url = f"{EVOLUTION_API_URL}/message/sendText/hana_intel"
            headers = {
                "apikey": EVOLUTION_API_TOKEN,
                "Content-Type": "application/json"
            }
            # Se fosse email, chamaríamos API do AWS SES ou SendGrid
            # Exemplo usando Evolution (WhatsApp/Imessage):
            safe_number = target_number if target_number else "5511999999999" # Mock fallback
            
            data = {
                "number": safe_number,
                "text": campaign.generated_content
            }
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=headers, json=data, timeout=10.0)
                resp.raise_for_status()
                
            # Disparo Concluído! Marca Anti-Fadiga no Redis (48h = 172800s)
            logger.info("Campanha disparada com sucesso.")
            if target_number:
                r.setex(fatigue_key, 172800, "locked")
                
            campaign.status = CampaignStatus.delivered
            
        except Exception as e:
            logger.error(f"Erro no envio da campanha: {str(e)}")
            campaign.status = CampaignStatus.failed_or_bounced
            
        # Atualiza Status Final
        await db.commit()


@celery_app.task(name="tasks.publish_campaign")
def publish_campaign_task(campaign_id: int):
    """
    Recebe as ordens de disparo (Aprovação) do painel e executa assíncronamente
    """
    logger.info("Celery [publish_campaign_task] iniciada.")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_campaign_dispatch(campaign_id))
    return {"status": "success", "campaign_id": campaign_id}
