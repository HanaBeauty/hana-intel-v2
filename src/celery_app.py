import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Inicializa o aplicativo Celery
celery_app = Celery(
    "hana_v2_worker",
    broker=REDIS_URL,
    include=["src.tasks"]
)

# Configurações otimizadas para tarefas de IA (Long-running)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=False,
    task_track_started=True,
    worker_prefetch_multiplier=1, # Para tarefas demoradas (LLMs), não dar prefetch
    task_ignore_result=True, # Ignora armazenamento de resultados reduzindo erros de backend do Redis
)
