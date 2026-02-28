import time
import logging
from .celery_app import celery_app
from .agents_crew import crew_content_lab

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
    return {"status": "success", "result": resultado_crew}
