import time
import logging
from .celery_app import celery_app
from .agents_crew import crew_content_lab, crew_social_media

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="src.tasks.process_strategic_intent")
def process_strategic_intent(self, user_intent: str):
    """
    Tarefa de background base para processar intents pesados.
    Executa o CrewAI (Sub-Agentes) sem travar a API.
    """
    logger.info(f"🚀 [Celery Worker] Iniciando processamento do intent: {user_intent}")
    
    # Executa o esquadrão de redação da Hana Beauty
    resultado_crew = crew_content_lab.process_campaign(user_intent)
    
    logger.info(f"✅ [Celery Worker] Tarefa concluída.")
    logger.info(f"✅ [Celery Worker] Tarefa concluída.")
    return {"status": "success", "result": resultado_crew}

@celery_app.task(bind=True, name="src.tasks.process_n8n_webhook_task")
def process_n8n_webhook_task(self, payload: dict):
    """
    Tarefa de background que processa os webhooks recebidos do N8N.
    Aqui os agentes do CrewAI podem ser instanciados de forma segura
    sem segurar a requisição HTTP original.
    """
    event_type = payload.get('event_type')
    logger.info(f"⚙️ [Celery Worker] Processando webhook N8N assincronamente: {event_type}")
    
    if event_type == "SOCIAL_COMMENT":
        logger.info("📱 Disparando Agente Community Manager para responder comentário...")
        social_context = payload.get("data", {})
        resposta = crew_social_media.process_social_comment(social_context)
        logger.info(f"✅ [Celery Worker] Resposta Social Gerada: {resposta}")
        # Futuro: Aqui faríamos um HTTP POST de volta pro N8N publicar a 'resposta'
        return {"status": "success", "event": event_type, "agent_response": resposta}
        
    elif event_type == "ABANDONED_CART":
        logger.info("🛒 Disparando Agente Copywriter para recuperação de carrinho...")
        # Lógica de carrinho
        import time
        time.sleep(2)
        return {"status": "success", "event": event_type}
        
    else:
        logger.warning(f"⚠️ Evento N8N desconhecido: {event_type}")
        return {"status": "ignored", "event": event_type}
