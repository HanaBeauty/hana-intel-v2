from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
import logging
from src.tasks import process_n8n_webhook_task

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v2/webhooks",
    tags=["Webhooks N8N"]
)

@router.post("/n8n")
async def n8n_webhook_receiver(request: Request):
    """
    Endpoint principal para receber disparos passivos (Webhooks) do N8N.
    Exemplo: Novo Lead no Facebook, Abandono de Carrinho capturado pelo N8N, etc.
    O processamento cognitivo será empurrado para o Celery (Background) para
    garantir que a API responda 200 OK instaantaneamente.
    """
    try:
        payload = await request.json()
        logger.info(f"📥 Recebido Webhook do N8N. Evento: {payload.get('event_type', 'Desconhecido')}")
        
        # Repassando o fardo pesado (CrewAI / LLM) para a fila assíncrona do Celery
        task = process_n8n_webhook_task.delay(payload)
        
        return {
            "status": "received", 
            "message": "Webhook recebido e enfileirado para processamento assíncrono.",
            "task_id": task.id
        }
        
    except Exception as e:
        logger.error(f"❌ Falha ao processar payload do N8N: {str(e)}")
        raise HTTPException(status_code=400, detail="Formato de Payload Inválido")
