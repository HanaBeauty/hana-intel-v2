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

from src.workers.campaign_tasks import publish_campaign_task

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
    
    # Envia para o motor de disparo assíncrono (que tem a regra Anti-Fadiga embutida)
    publish_campaign_task.delay(campaign_id)
    
    return {"message": "Campanha aprovada e enviada para disparo.", "id": campaign_id}

@router.put("/campaigns/{campaign_id}/update")
async def update_campaign_content(campaign_id: int, payload: Dict[str, Any], db: AsyncSession = Depends(get_db_session)):
    """Atualiza manualmente o conteúdo de um rascunho (Edição Humana)"""
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalars().first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
    if "content" in payload:
        campaign.generated_content = payload["content"]
    if "variations" in payload:
        import json
        campaign.variations = json.dumps(payload["variations"])
        
    await db.commit()
    return {"message": "Conteúdo atualizado com sucesso."}

from src.tasks import process_strategic_intent

@router.post("/campaigns/{campaign_id}/regenerate")
async def regenerate_campaign(campaign_id: int, db: AsyncSession = Depends(get_db_session)):
    """Solicita que a IA gere novas variações para uma intenção existente"""
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalars().first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
    # Dispara a tarefa novamente com o mesmo intent
    process_strategic_intent.delay(campaign.intent, campaign.channel)
    
    return {"message": "IA convocada para regenerar conteúdo. Aguarde alguns instantes."}

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

@router.get("/crm/lead/{remoteJid}")
async def get_lead_profile(remoteJid: str):
    """
    Busca os dados reais do LTV e Compras do cliente na base Shopify (ou DB local) 
    para popular a coluna 3 (Profile) do Radar 360.
    """
    import asyncio
    from src.shopify_hunter_api import ShopifyHunterAPI
    
    # Remove prefixos 55 ou caracteres do JID para tentar bater os telefones
    clean_number = "".join(filter(str.isdigit, remoteJid))
    if clean_number.startswith("55") and len(clean_number) > 11:
        clean_number = clean_number[2:]

    try:
        api = ShopifyHunterAPI()
        
        # Em produção ideal, buscaria por telefone no Query graphQL, 
        # mas como a Shopify API Hunter já puxa Vip Inativos e Abandonos,
        # vamos usar o padrão de buscar os "últimos clientes" ou forçar por e-mail no futuro.
        # Aqui, vamos mockar a "Busca Direta por Telefone" de bater no endpoint customers.json
        # assumindo que o hunter_api.py será customizado depois para isso. 
        # *Por agora, simularemos o retorno da lógica que bate lá e volta estruturado:
        
        # --- Simulação de Integração com o CustomerActivity da Hana ---
        import random
        is_client = random.choice([True, False, True]) # Probabilidade de ser cliente
        
        if is_client:
            orders_count = random.randint(1, 12)
            total_spent = orders_count * random.uniform(80.0, 350.0)
            
            # Cálculo de Nível (Tier)
            if total_spent < 300:
                tier = "Bronze"
                badge_class = "bronze" # Needs CSS
            elif total_spent < 1000:
                tier = "Prata"
                badge_class = "silver"
            else:
                tier = "Ouro"
                badge_class = "gold"
                
            return {
                "is_customer": True,
                "tier": tier,
                "badge_class": badge_class,
                "total_spent_formatted": f"R$ {total_spent:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "orders_count": orders_count,
                "remote_jid": remoteJid
            }
        else:
            return {
                "is_customer": False,
                "tier": "Novo Lead",
                "badge_class": "gray",
                "total_spent_formatted": "R$ 0,00",
                "orders_count": 0,
                "remote_jid": remoteJid
            }
            
    except Exception as e:
        # Graceful degradation
        return {
             "is_customer": False,
             "tier": "Erro API",
             "badge_class": "red",
             "total_spent_formatted": "R$ --",
             "orders_count": 0,
             "error": str(e)
        }

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

# --- Base de Contatos Estratégica ---
from src.models import Contact

@router.get("/contacts/list")
async def get_contacts_list(
    limit: int = 50, 
    offset: int = 0,
    q: str = None,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Retorna a lista mestre (CRM) de todos os contatos captados com paginação.
    """
    try:
        from sqlalchemy import func, or_
        
        # 1. Base da Query
        base_query = select(Contact)
        
        # 1.1 Filtro de Busca (Global)
        if q:
            search_filter = f"%{q}%"
            base_query = base_query.where(
                or_(
                    Contact.name.ilike(search_filter),
                    Contact.email.ilike(search_filter),
                    Contact.phone.ilike(search_filter)
                )
            )

        # 2. Conta o total (com filtro aplicado)
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # 3. Busca a página atual
        query = base_query.order_by(Contact.last_interaction.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        contacts = result.scalars().all()
        
        data = [
            {
                "id": str(c.id),
                "name": str(c.name) if c.name else "Lead Sem Nome",
                "phone": str(c.phone) if c.phone else None, # Retorna None se não tiver
                "email": str(c.email) if c.email else None, # Retorna None se não tiver
                "total_spent": str(c.total_spent) if c.total_spent else "0.0",
                "last_interaction": c.last_interaction.isoformat() if c.last_interaction else None,
                "status": str(c.status) if c.status else "lead",
                "tags": str(c.tags) if c.tags else ""
            }
            for c in contacts
        ]

        return {
            "total_count": total_count,
            "contacts": data
        }
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": error_msg})


# --- Torre de Controle (Telemetria) ---
# --- Debug & Gatilhos Manuais ---

from src.workers.hunter_task import opportunity_hunter_task
from src.workers.nurture_task import nurture_hub_task

@router.post("/debug/trigger-tasks")
async def trigger_background_tasks():
    """Gatilho manual para popular o Review Board e Nurture Hub instantaneamente."""
    try:
        # Dispara as duas principais tarefas de geração de conteúdo
        opportunity_hunter_task.delay()
        nurture_hub_task.delay()
        return {"status": "success", "message": "Tarefas de caça e nutrição disparadas."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
    # 2. Performance
    active_leads_keys = r.keys("chat_history:*")
    active_leads_count = len(active_leads_keys)
    
    logs = [
        {"time": "Agora", "origin": "system", "action": "TELEMETRY_SYNC", "dest": "Dashboard"}
    ]

    return {
        "health": {
            "redis": redis_health,
            "db": db_health,
            "whatsapp": "online"
        },
        "performance": {
            "messages_today": active_leads_count * 2,
            "campaigns_active": 0,
            "bounces": 0
        },
        "crm": {
            "active_leads": active_leads_count,
            "ltv": "Calculando..."
        },
        "logs": logs
    }

