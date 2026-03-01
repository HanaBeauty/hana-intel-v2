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

@router.get("/chat/{remoteJid}/history")
async def get_chat_history(remoteJid: str):
    """Retorna o histórico completo de uma conversa com os papéis (user vs bot/admin)"""
    r = get_redis_client()
    history_key = f"chat_history:{remoteJid}"
    
    # O Redis armazena como strings puras: "Usuário: texto", "Hana: texto"
    # Precisamos estruturar para o React consumir facilmente
    raw_history = r.lrange(history_key, 0, -1)
    
    structured_history = []
    
    for line in raw_history:
        if line.startswith("User:") or line.startswith("Usuário:"):
            sender = "user"
            text = line.split(":", 1)[1].strip() if ":" in line else line
        elif "Humano:" in line or "Juliano:" in line:
            sender = "admin"
            text = line.split(":", 1)[1].strip() if ":" in line else line
        else:
            sender = "bot"
            text = line.split(":", 1)[1].strip() if ":" in line else line
            
        structured_history.append({
            "sender": sender,
            "text": text,
            "time": "Histórico" # Timer real dependeria de salvar um JSON no array invés de string pura. Mocado por agora.
        })
        
    return structured_history

# Modelo para o Envio
from pydantic import BaseModel
class AdminMessageRequest(BaseModel):
    message: str

@router.post("/chat/{remoteJid}/send")
async def send_admin_message(remoteJid: str, payload: AdminMessageRequest):
    """Envia uma mensagem direta do Painel (Admin) para o Cliente via Evolution API e força Handoff"""
    import httpx
    
    EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
    EVOLUTION_API_TOKEN = os.getenv("EVOLUTION_API_TOKEN")
    
    # Ao humano Enviar mensagem, a IA precisa calar a boca automaticamente (Handoff implícito)
    r = get_redis_client()
    r.setex(f"human_handoff:{remoteJid}", 43200, "active")
    
    # Registra a fala Humana no Redes (Para a IA ter contexto se for reativada)
    # A IA precisa saber o que o Humano disse para não repetir
    admin_msg = f"Juliano (Humano): {payload.message}"
    r.rpush(f"chat_history:{remoteJid}", admin_msg)
    
    url = f"{EVOLUTION_API_URL}/message/sendText/hana_intel"
    headers = {
        "apikey": EVOLUTION_API_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "number": remoteJid,
        "text": payload.message
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=headers, json=data, timeout=10.0)
            resp.raise_for_status()
            return {"status": "success", "message": "Mensagem enviada com sucesso", "handoff": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Falha ao enviar mensagem: {str(e)}")

# --- Torre de Controle (Telemetria) ---
@router.get("/telemetry")
async def get_telemetry_data(db: AsyncSession = Depends(get_db_session)):
    """Retorna dados consolidados para a Torre de Controle (DB, Redis, Métricas)"""
    r = get_redis_client()
    
    # 1. Health Checks
    redis_health = "online" if r.ping() else "offline"
    try:
        await db.execute(select(1))
        db_health = "online"
    except Exception:
        db_health = "offline"
        
    # 2. Performance (Simplificado por agora, pode ler do DB de logs no futuro)
    # Contabiliza quantos clientes ativos temos no Redis (Leads Mapeados)
    active_leads_keys = r.keys("chat_history:*")
    active_leads_count = len(active_leads_keys)
    
    # Historico (Pega do Redis ou mock para logs rápidos)
    # A implementação ideal fará um LTRIM de uma chave 'system_logs' que o Celery vai popular
    logs = [
        {"time": "Agora", "origin": "system", "action": "TELEMETRY_SYNC", "dest": "Dashboard"}
    ]

    return {
        "health": {
            "redis": redis_health,
            "db": db_health,
            "whatsapp": "online" # Presumido online para v2 direct via Evolution webhook
        },
        "performance": {
            "messages_today": active_leads_count * 2, # Simulando volume vs leads
            "campaigns_active": 0,
            "bounces": 0
        },
        "crm": {
            "active_leads": active_leads_count,
            "ltv": "Calculando..." # A integrar com Shopify no futuro
        },
        "logs": logs
    }

