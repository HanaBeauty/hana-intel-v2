import os
import redis
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db_session
from src.models import Campaign, CampaignStatus

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard V2"])

# --- CRM & Campanhas ---

@router.get("/campaigns/pending")
async def get_pending_campaigns(db: AsyncSession = Depends(get_db_session)):
    """Retorna todas as campanhas geradas pela IA que aguardam aprovação humana."""
    query = select(Campaign).where(Campaign.status == CampaignStatus.draft).order_by(Campaign.created_at.desc())
    result = await db.execute(query)
    campaigns = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "title": c.title,
            "intent": c.intent,
            "channel": c.channel,
            "audience": c.target_audience,
            "content": c.generated_content,
            "status": c.status.value,
            "created_at": c.created_at
        }
        for c in campaigns
    ]

@router.post("/campaigns/{campaign_id}/approve")
async def approve_campaign(campaign_id: int, db: AsyncSession = Depends(get_db_session)):
    """Aprova uma campanha e a envia para a fila de disparo (Celery)"""
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalars().first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
    campaign.status = CampaignStatus.approved
    await db.commit()
    
    # Aqui chamaremos a Task Celery de Disparo (a ser implementada)
    # publish_campaign_task.delay(campaign_id)
    
    return {"message": "Campanha aprovada e enviada para disparo.", "id": campaign_id}

# --- Radar 360 (WhatsApp Live) ---

def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(redis_url, decode_responses=True)

@router.get("/chat/active")
async def get_active_chats():
    """Varre o Redis buscando quem a IA atendeu recentemente e o status de Hand-off"""
    r = get_redis_client()
    
    # Pegar todos os históricos de chat (Padrão: chat_history:5511999999999)
    keys = r.keys("chat_history:*")
    active_chats = []
    
    for key in keys:
        number = key.split(":")[1]
        history = r.lrange(key, -1, -1) # Pega só a última mensagem
        last_msg = history[0] if history else ""
        
        # Checar se a IA está silenciada para esse número
        is_handoff = r.exists(f"human_handoff:{number}")
        
        active_chats.append({
            "id": number,
            "name": f"Cliente {number[-4:]}", # Mock name for now
            "status": "handoff" if is_handoff else "bot_active",
            "lastMsg": last_msg
        })
        
    return active_chats

class HandoffRequest(Dict):
    pass

@router.post("/handoff/{number}/{action}")
async def toggle_handoff(number: str, action: str):
    """Ativa ou desativa a IA para um número específico via Dashboard (/bot_on e /bot_off)"""
    r = get_redis_client()
    handoff_key = f"human_handoff:{number}"
    
    if action == "enable_bot":
        r.delete(handoff_key)
        # Limpa o histórico sujo se necessário ou só religa
        return {"message": f"IA Reativada para {number}."}
    elif action == "disable_bot":
        r.setex(handoff_key, 43200, "active") # 12 horas
        return {"message": f"IA Silenciada (Hand-off ativado) para {number}."}
    else:
        raise HTTPException(status_code=400, detail="Ação inválida")
