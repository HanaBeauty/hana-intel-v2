from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any
import logging
import os
from src.tasks import process_strategic_intent
from src.routers import webhooks

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

# Registrando módulos independentes (Routers)
from src.routers import dashboard_api
app.include_router(webhooks.router)
app.include_router(dashboard_api.router)

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
    content_type: str = "conteúdo geral"

@app.post("/api/v1/intent", tags=["Hana AI Core"])
async def process_intent_sync(request: IntentRequest) -> Dict[str, Any]:
    """Processa a intenção do usuário online (não recomendado para tarefas longas)."""
    result = await manager.process_intent(request.intent)
    return result

@app.post("/api/v2/intent/async", tags=["Hana AI Core Background"])
async def process_intent_async(request: IntentRequest) -> Dict[str, Any]:
    """Enfileira a intenção no Redis via Celery e libera o usuário instantaneamente."""
    task = process_strategic_intent.delay(request.intent, request.content_type)
    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Tarefa de orquestração agendada com sucesso. A UI será notificada assim que a IA terminar."
    }

# ---------------------------------------------------------
# ROTEAMENTO FRONTEND REACT VITE (DASHBOARD V2.0)
# ---------------------------------------------------------
# Verifica se a pasta dist existe (Em produção no container Docker)
frontend_dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")

if os.path.exists(frontend_dist_path):
    # Monta todos os arquivos estáticos primeiro (/assets, vite.svg, etc)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="assets")
    
    # Catch-All para o React Router (Qualquer rota que não seja /api devolve o index.html do Vite)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react_app(full_path: str):
        # Evita conflitos com rotas da api
        if full_path.startswith("api/"):
            return {"error": "API route not found"}
        
        # Pode ser que o app peça um favicon na raiz, serve direto
        potential_file = os.path.join(frontend_dist_path, full_path)
        if os.path.isfile(potential_file):
            return FileResponse(potential_file)
            
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))
else:
    logger.warning("⚠️ Diretório 'frontend/dist' não encontrado. O React Dashboard NÃO será servido pela FastAPI.")
