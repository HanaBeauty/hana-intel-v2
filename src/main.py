from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hana Intel 2.0",
    description="Ecossistema Multi-Agent de CRM e Automação (Assíncrono)",
    version="2.0.0"
)

# CORS Middleware (permitir comunicação com futuro painel Vue/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    return {"message": "Hana Intel 2.0 API is running."}

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    # Placeholder para checagens futuras (Redis, DB)
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "api": "ok",
            "redis": "pending_setup",
            "database": "pending_setup"
        }
    }
from pydantic import BaseModel
from .agent import manager
from .tasks import process_strategic_intent

class IntentRequest(BaseModel):
    intent: str

@app.post("/api/v1/intent", tags=["Hana AI Core"])
async def process_intent_sync(request: IntentRequest) -> Dict[str, Any]:
    """Processa a intenção do usuário online (não recomendado para tarefas longas)."""
    result = await manager.process_intent(request.intent)
    return result

@app.post("/api/v2/intent/async", tags=["Hana AI Core Background"])
async def process_intent_async(request: IntentRequest) -> Dict[str, Any]:
    """Enfileira a intenção no Redis via Celery e libera o usuário instantaneamente."""
    task = process_strategic_intent.delay(request.intent)
    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Tarefa de orquestração agendada com sucesso. A UI será notificada assim que a IA terminar."
    }
