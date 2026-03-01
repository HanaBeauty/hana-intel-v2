from fastapi import APIRouter, Body, HTTPException, Request
from typing import Dict, Any
import logging
from src.tasks import process_evolution_webhook_task

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v2/webhooks",
    tags=["Webhooks"]
)

@router.post("/evolution")
async def evolution_webhook_receiver(request: Request, payload: Dict[str, Any] = Body(default={})):
    """
    Endpoint principal para receber eventos (Webhooks) da Evolution API (WhatsApp).
    """
    try:
        # Pega o tipo de evento (ex: messages.upsert)
        event_type = payload.get('event', 'Desconhecido')
        logger.info(f"📥 Recebido Webhook Evolution API. Evento: {event_type}")
        
        # O Celery fará o processamento pesado
        task = process_evolution_webhook_task.delay(payload)
        task_id = getattr(task, 'id', str(task))
        
        return {
            "status": "received", 
            "message": "Webhook da Evolution recebido e enfileirado.",
            "task_id": task_id
        }
        
    except Exception as e:
        logger.error(f"❌ Falha ao processar payload da Evolution API: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro interno HTTP Post: {str(e)}")

@router.post("/shopify")
async def shopify_webhook_receiver(payload: Dict[str, Any] = Body(...)):
    """
    Placeholder para webhooks nativos da Shopify (Carrinhos Abandonados, Pedidos)
    """
    return {"status": "received", "message": "Shopify webhook ack"}
